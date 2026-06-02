import os
import re
import ast
import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from slugify import slugify

BASE = "https://buildai.substack.com"
INDEX_URL = "https://buildai.substack.com/p/build-ai-modules"

OUTPUT_DIR = "buildai-course"
CACHE_DIR = ".cache"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------
# Fetch + cache
# -------------------------

def fetch(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, slugify(url) + ".html")

    if os.path.exists(path):
        return open(path).read()

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    with open(path, "w") as f:
        f.write(r.text)

    return r.text


# -------------------------
# Index parsing
# -------------------------

def get_units():
    html = fetch(INDEX_URL)
    soup = BeautifulSoup(html, "html.parser")

    units = []
    current = []

    for el in soup.find_all(["h1", "h2", "h3", "a"]):
        if el.name in ["h1", "h2", "h3"]:
            if "unit" in el.get_text().lower():
                if current:
                    units.append(current)
                current = []

        elif el.name == "a":
            href = el.get("href", "")
            if href.startswith("/p/") and "build-ai-modules" not in href:
                current.append(urljoin(BASE, href))

    if current:
        units.append(current)

    return units


# -------------------------
# HTML → Markdown
# -------------------------

def html_to_markdown(html):
    md = trafilatura.extract(html, output_format="markdown")
    if not md:
        raise ValueError("Markdown extraction failed")
    return md


# -------------------------
# Filename inference (no LLM)
# -------------------------

def infer_filename(code, lang, index):
    lang = (lang or "").lower()

    ext_map = {
        "python": "py",
        "py": "py",
        "javascript": "js",
        "js": "js",
        "typescript": "ts",
        "ts": "ts",
        "bash": "sh",
        "shell": "sh",
    }

    ext = ext_map.get(lang, lang if lang else "txt")

    lines = code.strip().split("\n")
    first = lines[0].strip() if lines else ""

    # explicit filename comment
    m = re.match(r"(#|//)\s*filename:\s*(\S+)", first, re.I)
    if m:
        return m.group(2)

    # Python AST
    if ext == "py":
        try:
            tree = ast.parse(code)

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    return f"{node.name}.py"

            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    return f"{node.name}.py"

        except Exception:
            pass

    # JS / TS
    if ext in ["js", "ts"]:
        patterns = [
            r"class\s+([a-zA-Z0-9_]+)",
            r"function\s+([a-zA-Z0-9_]+)",
            r"const\s+([a-zA-Z0-9_]+)\s*=",
        ]
        for p in patterns:
            m = re.search(p, code)
            if m:
                return f"{m.group(1)}.{ext}"

    # fallback: first meaningful line
    for line in lines:
        line = line.strip()
        if line:
            name = re.sub(r"\W+", "_", line.lower())[:40]
            return f"{name}.{ext}"

    return f"block_{index}.{ext}"


# -------------------------
# Markdown rewrite
# -------------------------

CODE_BLOCK = r"```(\w+)?\n(.*?)```"

def rewrite_markdown(md, code_dir):
    os.makedirs(code_dir, exist_ok=True)

    new_md = []
    last = 0
    used = set()

    for i, m in enumerate(re.finditer(CODE_BLOCK, md, re.DOTALL)):
        start, end = m.span()
        lang = m.group(1) or "txt"
        code = m.group(2).strip()

        filename = infer_filename(code, lang, i)

        # dedupe
        base, ext = os.path.splitext(filename)
        counter = 1
        while filename in used:
            filename = f"{base}_{counter}{ext}"
            counter += 1

        used.add(filename)

        filepath = os.path.join(code_dir, filename)
        with open(filepath, "w") as f:
            f.write(code)

        new_md.append(md[last:start])
        new_md.append(f"\n📄 [`{filename}`](./code/{filename})\n")

        last = end

    new_md.append(md[last:])
    return "".join(new_md)


# -------------------------
# Post processing
# -------------------------

def process_post(url, unit_idx, post_idx):
    html = fetch(url)

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else f"post-{post_idx}"

    slug = slugify(title)

    base_path = os.path.join(
        OUTPUT_DIR,
        f"unit-{unit_idx:02d}",
        f"post-{post_idx:02d}-{slug}"
    )

    code_path = os.path.join(base_path, "code")
    os.makedirs(base_path, exist_ok=True)

    md = html_to_markdown(html)
    clean_md = rewrite_markdown(md, code_path)

    with open(os.path.join(base_path, "post.md"), "w") as f:
        f.write(clean_md)


# -------------------------
# Main
# -------------------------

def main():
    units = get_units()

    for u_idx, posts in enumerate(units, start=1):
        for p_idx, url in enumerate(posts, start=1):
            print(f"Unit {u_idx} Post {p_idx}: {url}")
            process_post(url, u_idx, p_idx)


if __name__ == "__main__":
    main()
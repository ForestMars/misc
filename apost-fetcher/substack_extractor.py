#!/usr/bin/env python3
"""
BUILD AI Substack Code Extractor
─────────────────────────────────
Reads the series index at buildai.substack.com/p/build-ai-modules,
fetches every linked post, extracts fenced code blocks, names them
with Claude, and writes a clean directory tree:

  buildai_repo/
  ├── module_1_foundation_model_training/
  │   ├── unit_1_distributed_training/
  │   │   ├── 01_tensor_parallelism/
  │   │   │   ├── naive_multi_head_attention.py
  │   │   │   ├── tensor_parallel_attention.py
  │   │   │   └── post.md   ← prose only, code replaced with links
  │   │   └── 02_pipeline_parallelism/
  │   │       └── ...
  │   └── unit_2_data_pipeline/
  │       └── ...
  └── ...
"""

import os, re, time, json
import requests
import anthropic
from pathlib import Path
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
INDEX_URL  = "https://buildai.substack.com/p/build-ai-modules"
OUTPUT_DIR = Path("./buildai_repo")
SLEEP      = 1.5          # seconds between HTTP requests — be polite
# ─────────────────────────────────────────────────────────────────────────────

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env

CODE_FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


# ── Step 1: Parse the index page ──────────────────────────────────────────────

def parse_index(url: str) -> list[dict]:
    """
    Returns a flat list of posts, each with:
      module_num, module_title, unit_num, unit_title,
      post_num (within unit), post_title, url
    """
    print(f"Fetching index: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    posts      = []
    module_num = 0
    unit_num   = 0
    post_num   = 0
    cur_module = ""
    cur_unit   = ""

    for tag in soup.find_all(["h2", "h3", "li"]):
        text = tag.get_text(strip=True)
        if not text:
            continue

        if tag.name == "h2" and "Module" in text:
            module_num += 1
            unit_num    = 0
            cur_module  = text
            continue

        if tag.name == "h3" and "Unit" in text:
            unit_num += 1
            post_num  = 0
            cur_unit  = text
            continue

        if tag.name == "li":
            a = tag.find("a", href=True)
            if a and "buildai.substack.com/p/" in a["href"]:
                post_num += 1
                posts.append({
                    "module_num":   module_num,
                    "module_title": cur_module,
                    "unit_num":     unit_num,
                    "unit_title":   cur_unit,
                    "post_num":     post_num,
                    "post_title":   a.get_text(strip=True),
                    "url":          a["href"].split("?")[0],
                })

    print(f"  → Found {len(posts)} linked posts\n")
    return posts


# ── Step 2: Fetch a post and return markdown-ified text ───────────────────────

def fetch_post_text(url: str) -> str | None:
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        print(f"    ⚠  HTTP {resp.status_code} — skipping")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    body = (soup.find("div", class_=re.compile(r"available-content", re.I))
            or soup.find("div", class_=re.compile(r"body\s+markup", re.I))
            or soup.find("article")
            or soup.body)

    if body is None:
        return None

    # Convert <pre><code> blocks to fenced markdown before text extraction
    for pre in body.find_all("pre"):
        code = pre.find("code")
        raw  = (code or pre).get_text()
        lang = ""
        if code and code.get("class"):
            for cls in code["class"]:
                if cls.startswith("language-"):
                    lang = cls[9:]
                    break
        pre.replace_with(f"\n```{lang}\n{raw.strip()}\n```\n")

    return body.get_text("\n")


# ── Step 3: Extract fenced code blocks ───────────────────────────────────────

def extract_code_blocks(text: str) -> list[dict]:
    return [
        {"lang": (m.group(1) or "").strip(), "code": m.group(2).strip()}
        for m in CODE_FENCE_RE.finditer(text)
        if m.group(2).strip()
    ]


# ── Step 4: Ask Claude to name each file ─────────────────────────────────────

SYSTEM_PROMPT = """\
You are a code organisation assistant. Given a blog post title and a list of
fenced code blocks (with optional language hints), return ONLY a JSON array
where each element corresponds to one code block in the same order:
  {
    "filename": "<descriptive_snake_case_name.ext>",
    "description": "<one sentence: what this specific snippet does>"
  }

Rules:
- filename must be descriptive and unique within this post.
- Use the correct extension: .py .js .ts .sh .yaml .json etc.
- Descriptions must be specific, not generic ("code from the article").
- Return ONLY the JSON array. No markdown fences, no explanation.
"""

def name_files_with_claude(post_title: str, blocks: list[dict]) -> list[dict] | None:
    items = []
    for i, b in enumerate(blocks, 1):
        lang_note = f" (language: {b['lang']})" if b["lang"] else ""
        items.append(f"### Block {i}{lang_note}\n```\n{b['code']}\n```")

    user_msg = f"Post title: {post_title}\n\n" + "\n\n".join(items)

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = resp.content[0].text.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"    ✗ Claude error: {e}")
        return None


# ── Step 5: Build post.md — prose with code blocks replaced by file links ─────

def build_post_md(raw_text: str, post_title: str,
                  post_url: str, blocks: list[dict],
                  file_meta: list[dict]) -> str:
    md     = raw_text
    offset = 0

    for m, meta in zip(CODE_FENCE_RE.finditer(raw_text), file_meta):
        fname = meta["filename"]
        desc  = meta.get("description", "")
        link  = f"\n📄 **[`{fname}`](./{fname})**"
        if desc:
            link += f"  \n*{desc}*\n"

        start  = m.start() + offset
        end    = m.end()   + offset
        md     = md[:start] + link + md[end:]
        offset += len(link) - (m.end() - m.start())

    header = (f"# {post_title}\n\n"
              f"*Source: [{post_url}]({post_url})*\n\n---\n\n")
    return header + md


# ── Step 6: Write everything to disk ─────────────────────────────────────────

def slugify(text: str, max_len: int = 40) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:max_len]


def write_post(post: dict, raw_text: str,
               blocks: list[dict], file_meta: list[dict]):
    mod_slug  = slugify(re.sub(r"^Module\s+\w+[:\-]\s*", "", post["module_title"]))
    unit_slug = slugify(re.sub(r"^Unit\s+\d+[:\-]\s*", "",  post["unit_title"]))
    post_slug = slugify(post["post_title"])

    mod_dir  = f"module_{post['module_num']}_{mod_slug}"
    unit_dir = f"unit_{post['unit_num']}_{unit_slug}"
    post_dir = f"{post['post_num']:02d}_{post_slug}"

    dir_path = OUTPUT_DIR / mod_dir / unit_dir / post_dir
    dir_path.mkdir(parents=True, exist_ok=True)

    # Write code files (de-duplicate names)
    used: set[str] = set()
    resolved = []
    for block, meta in zip(blocks, file_meta):
        fname = meta["filename"]
        base, ext = os.path.splitext(fname)
        counter = 1
        while fname in used:
            fname = f"{base}_{counter}{ext}"
            counter += 1
        used.add(fname)
        (dir_path / fname).write_text(block["code"], encoding="utf-8")
        print(f"      → {dir_path / fname}")
        resolved.append({**meta, "filename": fname})

    # Write post.md
    post_md = build_post_md(raw_text, post["post_title"],
                            post["url"], blocks, resolved)
    (dir_path / "post.md").write_text(post_md, encoding="utf-8")
    print(f"      → {dir_path / 'post.md'}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  BUILD AI Code Extractor  →  {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = parse_index(INDEX_URL)
    ok = skipped = 0

    for post in posts:
        print(f"[{post['module_num']}.{post['unit_num']}.{post['post_num']:02d}] "
              f"{post['post_title']}")
        print(f"  {post['url']}")
        time.sleep(SLEEP)

        raw = fetch_post_text(post["url"])
        if not raw:
            skipped += 1
            continue

        blocks = extract_code_blocks(raw)
        if not blocks:
            print("    – No code blocks, skipping\n")
            skipped += 1
            continue
        print(f"    {len(blocks)} code block(s) found")

        file_meta = name_files_with_claude(post["post_title"], blocks)
        if not file_meta or len(file_meta) != len(blocks):
            print("    ✗ Claude naming mismatch, skipping\n")
            skipped += 1
            continue

        write_post(post, raw, blocks, file_meta)
        ok += 1
        print()

    print(f"\n{'='*60}")
    print(f"  Done!  {ok} posts written,  {skipped} skipped.")
    print(f"  Output: {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

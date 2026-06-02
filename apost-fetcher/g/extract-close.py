#!/usr/bin/env python3
import os, re, time, requests
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# ── Config ────────────────────────────────────────────────────────────────────
INDEX_URL  = "https://buildai.substack.com/p/build-ai-modules"
OUTPUT_DIR = Path("./buildai_repo")
SLEEP      = 1.0  

def get_local_name(code_text: str, index: int, used_names: set) -> str:
    """Extracts a filename from the first class or function found in code."""
    match = re.search(r"(?:class|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)", code_text)
    base_name = match.group(1).lower() if match else f"snippet_{index}"
    filename = f"{base_name}.py"
    
    counter = 1
    while filename in used_names:
        filename = f"{base_name}_{counter}.py"
        counter += 1
    
    used_names.add(filename)
    return filename

def slugify(text: str) -> str:
    """Converts titles to filesystem-friendly names."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:50]

def run_pipeline():
    print(f"🚀 Starting extraction to: {OUTPUT_DIR.resolve()}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resp = requests.get(INDEX_URL, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    posts = []
    m_n, u_n, p_n = 0, 0, 0
    cur_m, cur_u = "Module", "Unit"

    for tag in soup.find_all(["h2", "h3", "li"]):
        text = tag.get_text(strip=True)
        if not text: continue
        
        if tag.name == "h2" and "Module" in text:
            m_n += 1
            u_n, cur_m = 0, text
        elif tag.name == "h3" and "Unit" in text:
            u_n += 1
            p_n, cur_u = 0, text
        elif tag.name == "li":
            a = tag.find("a", href=True)
            if a and "buildai.substack.com/p/" in a["href"]:
                p_n += 1
                posts.append({
                    "m_idx": m_n, "m_title": cur_m,
                    "u_idx": u_n, "u_title": cur_u,
                    "p_idx": p_n, "p_title": a.get_text(strip=True),
                    "url": a["href"].split("?")[0]
                })

    for p in posts:
        print(f"📦 Processing: {p['p_title']}")
        time.sleep(SLEEP)
        
        post_resp = requests.get(p['url'], timeout=15)
        if post_resp.status_code != 200: continue
        
        post_soup = BeautifulSoup(post_resp.text, "html.parser")
        body = post_soup.find("div", class_=re.compile(r"available-content|body", re.I)) or post_soup.article
        if not body: continue

        # Folder and File Names
        post_slug = slugify(p['p_title'])
        dir_path = OUTPUT_DIR / f"mod_{p['m_idx']}_{slugify(p['m_title'])}" / f"unit_{p['u_idx']}_{slugify(p['u_title'])}" / f"{p['p_idx']:02d}_{post_slug}"
        dir_path.mkdir(parents=True, exist_ok=True)

        used_filenames = []
        
        # 1. Process Code Blocks
        # We replace the <pre> tag with a VERY distinct unique ID to avoid markdownify escaping it
        for i, pre in enumerate(body.find_all("pre")):
            code_content = pre.get_text().strip()
            if not code_content: continue
            
            # Collect filename and write code file
            fname = get_local_name(code_content, i, set(used_filenames))
            used_filenames.append(fname)
            (dir_path / fname).write_text(code_content, encoding="utf-8")
            
            # Insert a "Marker" that won't get garbled by Markdown conversion
            # We use a simple P tag so markdownify treats it as a standard paragraph
            marker = post_soup.new_tag("p")
            marker.string = f"MARKER_START_{fname}_MARKER_END"
            pre.replace_with(marker)

        # 2. Convert to Markdown
        # This handles headers, TOC lists, and links correctly
        markdown_content = md(str(body), heading_style="ATX").strip()

        # 3. Post-Process: Swap markers for actual Markdown links
        # We use regex here to find the marker even if markdownify wrapped it in newlines
        for fname in used_filenames:
            pattern = rf"MARKER_START_{re.escape(fname)}_MARKER_END"
            replacement = f"\n\n📄 **[Code: {fname}](./{fname})**\n\n"
            markdown_content = re.sub(pattern, replacement, markdown_content)

        # 4. Save file with the Actual Title
        final_filename = f"{post_slug}.md"
        (dir_path / final_filename).write_text(f"# {p['p_title']}\n\n{markdown_content}", encoding="utf-8")

if __name__ == "__main__":
    run_pipeline()


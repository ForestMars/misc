#!/usr/bin/env python3
import os, re, time, requests
from pathlib import Path
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
INDEX_URL  = "https://buildai.substack.com/p/build-ai-modules"
OUTPUT_DIR = Path("./buildai_repo")
SLEEP      = 1.0  

def get_local_name(code_text: str, index: int, used_names: set) -> str:
    """Extracts a filename from the first class or function found in code."""
    # Look for 'class Name' or 'def name'
    match = re.search(r"(?:class|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)", code_text)
    
    base_name = match.group(1).lower() if match else f"snippet_{index}"
    filename = f"{base_name}.py"
    
    # Simple de-duplication
    counter = 1
    while filename in used_names:
        filename = f"{base_name}_{counter}.py"
        counter += 1
    
    used_names.add(filename)
    return filename

def run_pipeline():
    print(f"🚀 Starting extraction to: {OUTPUT_DIR.resolve()}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Parse the Index Post
    resp = requests.get(INDEX_URL, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    posts = []
    m_n, u_n, p_n = 0, 0, 0
    cur_m, cur_u = "Module", "Unit"

    # Identify hierarchy from h2 (Module), h3 (Unit), and li (Post)
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

    # 2. Process Posts
    for p in posts:
        print(f"📦 {p['m_idx']}.{p['u_idx']}.{p['p_idx']:02d} | {p['p_title']}")
        time.sleep(SLEEP)
        
        post_resp = requests.get(p['url'], timeout=15)
        if post_resp.status_code != 200: continue
        
        post_soup = BeautifulSoup(post_resp.text, "html.parser")
        body = post_soup.find("div", class_=re.compile(r"available-content|body", re.I)) or post_soup.article
        if not body: continue

        # Folder structure: module/unit/post
        slug = lambda x: re.sub(r"[^a-z0-9]+", "_", x.lower()).strip("_")[:30]
        dir_path = OUTPUT_DIR / f"mod_{p['m_idx']}_{slug(p['m_title'])}" / f"unit_{p['u_idx']}_{slug(p['u_title'])}" / f"{p['p_idx']:02d}_{slug(p['p_title'])}"
        dir_path.mkdir(parents=True, exist_ok=True)

        used_filenames = set()
        
        # Extract code blocks
        for i, pre in enumerate(body.find_all("pre")):
            code_content = pre.get_text().strip()
            if not code_content: continue
            
            fname = get_local_name(code_content, i, used_filenames)
            (dir_path / fname).write_text(code_content, encoding="utf-8")
            
            # Replace code block in HTML with a relative link
            link_tag = post_soup.new_tag("p")
            link_tag.string = f"\n\n📄 **[Code: {fname}](./{fname})**\n\n"
            pre.replace_with(link_tag)

        # Final Markdown save
        (dir_path / "post.md").write_text(f"# {p['p_title']}\n\n{body.get_text()}", encoding="utf-8")

if __name__ == "__main__":
    run_pipeline()

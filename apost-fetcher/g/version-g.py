import os, re, time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
INDEX_URL  = "https://buildai.substack.com/p/build-ai-modules"
OUTPUT_DIR = Path("./buildai_repo")
SLEEP      = 1.0  

# ── Step 1: Logic-Based Naming ──────────────────────────────────────────────

def get_local_name(code_text: str, index: int) -> str:
    """
    Parses code to find a logical filename. 
    Order of operations: 1. Class name, 2. Function name, 3. Shebang/Comment, 4. Index.
    """
    # Try to find a class definition
    class_match = re.search(r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)", code_text)
    if class_match:
        return f"{class_match.group(1).lower()}.py"

    # Try to find a function definition
    def_match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)", code_text)
    if def_match:
        return f"{def_match.group(1).lower()}.py"
    
    # Try to find a filename in a leading comment (e.g., # main.py)
    comment_match = re.search(r"^(?:#|//)\s*([\w\-\.]+\.(?:py|sh|js|ts))", code_text)
    if comment_match:
        return comment_match.group(1)

    # Fallback to index-based naming
    return f"snippet_{index}.py"

# ── Step 2: Index & Post Parsing ─────────────────────────────────────────────

def parse_index(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    posts = []
    module_num, unit_num, post_num = 0, 0, 0
    cur_module, cur_unit = "module", "unit"

    for tag in soup.find_all(["h2", "h3", "li"]):
        text = tag.get_text(strip=True)
        if not text: continue
        if tag.name == "h2" and "Module" in text:
            module_num += 1
            unit_num, cur_module = 0, text
        elif tag.name == "h3" and "Unit" in text:
            unit_num += 1
            post_num, cur_unit = 0, text
        elif tag.name == "li":
            a = tag.find("a", href=True)
            if a and "buildai.substack.com/p/" in a["href"]:
                post_num += 1
                posts.append({
                    "m_n": module_num, "m_t": cur_module,
                    "u_n": unit_num, "u_t": cur_unit,
                    "p_n": post_num, "p_t": a.get_text(strip=True),
                    "url": a["href"].split("?")[0]
                })
    return posts

def process_post(post):
    resp = requests.get(post['url'], timeout=15)
    if resp.status_code != 200: return
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Identify content area 
    body = soup.find("div", class_=re.compile(r"available-content|body", re.I)) or soup.article
    if not body: return

    # Setup directories
    slug = lambda x: re.sub(r"[^a-z0-9]+", "_", x.lower()).strip("_")[:30]
    path = OUTPUT_DIR / f"mod_{post['m_n']}_{slug(post['m_t'])}" / f"unit_{post['u_n']}_{slug(post['u_t'])}" / f"{post['p_n']:02d}_{slug(post['p_t'])}"
    path.mkdir(parents=True, exist_ok=True)

    # Extract code and replace with links
    code_blocks = body.find_all("pre")
    md_content = body.get_text("\n")
    
    for i, pre in enumerate(code_blocks):
        code_text = pre.get_text().strip()
        if not code_text: continue
        
        filename = get_local_name(code_text, i)
        (path / filename).write_text(code_text)
        
        # Simple string replacement for the "post.md" 
        link_text = f"\n\n📄 **[Code: {filename}](./{filename})**\n\n"
        md_content = md_content.replace(pre.get_text(), link_text)

    (path / "post.md").write_text(f"# {post['p_t']}\n\n{md_content}")

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_posts = parse_index(INDEX_URL)
    for p in all_posts:
        print(f"Processing {p['p_t']}...")
        process_post(p)
        time.sleep(SLEEP)
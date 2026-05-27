import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# BASE_URL = "https://triptomean.com/"
BASE_URL = "https://smarthub.my/"

# OUTPUT_DIR = "triptomean_mirror"
OUTPUT_DIR = "smarthub"

visited = {}

ASSET_TAGS = {
    'img':    ['src', 'srcset'],
    'script': ['src'],
    'link':   ['href'],
    'source': ['src', 'srcset'],
    'video':  ['src', 'poster'],
    'audio':  ['src'],
}

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0'

def get_sitemap_urls(sitemap_url):
    try:
        res = session.get(sitemap_url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        return [loc.text.strip() for loc in soup.find_all('loc')]
    except:
        return []

def get_local_path(url):
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == '/':
        return 'index.html'
    if not os.path.splitext(path)[1]:
        path = path.rstrip('/') + '/index.html'
    return path.lstrip('/')

def download(url):
    url = url.split('?')[0].split('#')[0].rstrip('/')
    if not url or url in visited:
        return visited.get(url)
    if not url.startswith(BASE_URL.rstrip('/')):
        # Still download off-site assets, but save flat into _assets/
        parsed = urlparse(url)
        local_path = os.path.join('_assets', parsed.netloc, parsed.path.lstrip('/'))
        if not local_path or local_path in visited.values():
            return local_path
    else:
        local_path = get_local_path(url)

    visited[url] = local_path
    full_local = os.path.join(OUTPUT_DIR, local_path)
    os.makedirs(os.path.dirname(full_local) or OUTPUT_DIR, exist_ok=True)

    print(f"  {'📄' if local_path.endswith('.html') else '📦'} {url}")
    try:
        res = session.get(url, timeout=15)
        if res.status_code == 404:
            visited[url] = None
            return None
        res.raise_for_status()

        # Don't save HTML responses as non-HTML files
        content_type = res.headers.get('Content-Type', '')
        if local_path.endswith('.css') and 'text/css' not in content_type:
            visited[url] = None
            return None
        if local_path.endswith('.js') and 'javascript' not in content_type:
            visited[url] = None
            return None

        with open(full_local, 'wb') as f:
            f.write(res.content)
            
        return local_path
    except Exception as e:
        print(f"    ✗ {e}")
        visited[url] = None
        return None

# ── Pass 1: crawl HTML pages ──────────────────────────────────────────────────
print("=== Pass 1: Crawling pages ===")

WIKI_SECTIONS = [
    "math", "rh", "qg", "grf", "rtsg", "companions", "monograph",
    "millennium", "mathematics", "agents", "meta", "deploy", "compute"
]

queue = list(set(
    [BASE_URL] +
    get_sitemap_urls("https://smarthub.my/sitemap.xml") +
    get_sitemap_urls("https://smarthub.my/wiki/sitemap.xml") +
    get_sitemap_urls("https://smarthub.my/wiki/math/sitemap.xml") + 
    [f"https://smarthub.my/wiki/{s}/" for s in WIKI_SECTIONS] +
    [f"https://smarthub.my/wiki/{s}/sitemap.xml" for s in WIKI_SECTIONS]
))



pages = []  # (url, local_path) for HTML files only

while queue:
    url = queue.pop(0).split('?')[0].split('#')[0].rstrip('/')
    if url in visited or not url.startswith(BASE_URL.rstrip('/')):
        continue

    local_path = download(url)
    if not local_path:
        continue

    full_local = os.path.join(OUTPUT_DIR, local_path)
    try:
        with open(full_local, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
    except:
        continue

    if '<html' not in html.lower():
        continue

    pages.append((url, local_path))
    soup = BeautifulSoup(html, 'html.parser')

    for a in soup.find_all('a', href=True):
        found = urljoin(url, a['href']).split('?')[0].split('#')[0].rstrip('/')
        if found.startswith(BASE_URL.rstrip('/')) and found not in visited:
            queue.append(found)

# ── Pass 2: download all assets ───────────────────────────────────────────────
print("\n=== Pass 2: Downloading assets ===")
for page_url, page_local in pages:
    full_local = os.path.join(OUTPUT_DIR, page_local)
    with open(full_local, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    for tag, attrs in ASSET_TAGS.items():
        for el in soup.find_all(tag):
            for attr in attrs:
                val = el.get(attr)
                if not val:
                    continue
                # handle srcset ("url 2x, url2 3x")
                if attr == 'srcset':
                    parts = []
                    for chunk in val.split(','):
                        bits = chunk.strip().split()
                        if bits:
                            asset_url = urljoin(page_url, bits[0])
                            local = download(asset_url)
                            if local:
                                bits[0] = os.path.relpath(
                                    os.path.join(OUTPUT_DIR, local),
                                    os.path.dirname(full_local)
                                )
                            parts.append(' '.join(bits))
                    el[attr] = ', '.join(parts)
                else:
                    asset_url = urljoin(page_url, val)
                    local = download(asset_url)
                    if local:
                        el[attr] = os.path.relpath(
                            os.path.join(OUTPUT_DIR, local),
                            os.path.dirname(full_local)
                        )

    # Also rewrite inline CSS url() references
    for style_tag in soup.find_all('style'):
        if style_tag.string:
            import re
            def rewrite_css_url(m):
                asset_url = urljoin(page_url, m.group(1).strip('\'"'))
                local = download(asset_url)
                if local:
                    return f"url('{os.path.relpath(os.path.join(OUTPUT_DIR, local), os.path.dirname(full_local))}')"
                return m.group(0)
            style_tag.string = re.sub(r'url\(([^)]+)\)', rewrite_css_url, style_tag.string)

    # Rewrite <a> links
    for a in soup.find_all('a', href=True):
        link_url = urljoin(page_url, a['href']).split('?')[0].split('#')[0].rstrip('/')
        if link_url in visited and visited[link_url]:
            a['href'] = os.path.relpath(
                os.path.join(OUTPUT_DIR, visited[link_url]),
                os.path.dirname(full_local)
            )

    with open(full_local, 'w', encoding='utf-8') as f:
        f.write(str(soup))

print(f"\n✅ Done. Open {os.path.join(OUTPUT_DIR, 'index.html')}")

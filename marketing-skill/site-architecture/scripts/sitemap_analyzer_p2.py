# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sitemap_analyzer_base import *  # noqa: F403,E402
# fmt: off
from sitemap_analyzer_p1 import detect_path_siblings, get_depth, get_path_pattern, looks_like_dynamic_url  # noqa: E402,E501
# fmt: on


def parse_sitemap(content: str) -> list:
    """Parse sitemap XML and return list of URL dicts."""
    urls = []

    # Strip namespace declarations for simpler parsing
    content_clean = re.sub(r'xmlns[^=]*="[^"]*"', '', content)

    try:
        root = ET.fromstring(content_clean)
    except ET.ParseError as e:
        print(f"❌ XML parse error: {e}", file=sys.stderr)
        return []

    # Handle sitemap index (points to other sitemaps)
    if root.tag.endswith("sitemapindex") or root.tag == "sitemapindex":
        print("ℹ️  This is a sitemap index file — it points to child sitemaps.")
        print("   Child sitemaps:")
        for sitemap in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") or root.findall(".//loc"):
            print(f"   - {sitemap.text}")
        print("   Run this tool on each child sitemap for full analysis.")
        return []

    # Regular urlset
    for url_el in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url") or root.findall(".//url"):
        loc_el = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") or url_el.find("loc")
        lastmod_el = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod") or url_el.find("lastmod")
        priority_el = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority") or url_el.find("priority")

        if loc_el is not None and loc_el.text:
            urls.append({
                "url": loc_el.text.strip(),
                "lastmod": lastmod_el.text.strip() if lastmod_el is not None and lastmod_el.text else None,
                "priority": float(priority_el.text.strip()) if priority_el is not None and priority_el.text else None,
            })

    return urls
def analyze_urls(urls: list) -> dict:
    raw_urls = [u["url"] for u in urls]
    paths = [urlparse(u).path for u in raw_urls]

    depths = [get_depth(p) for p in paths]
    depth_counter = Counter(depths)

    dynamic_urls = [u for u in raw_urls if looks_like_dynamic_url(u)]

    patterns = Counter(get_path_pattern(urlparse(u).path) for u in raw_urls)
    top_patterns = patterns.most_common(10)

    duplicate_slugs = detect_path_siblings(raw_urls)

    deep_urls = [(u, get_depth(urlparse(u).path)) for u in raw_urls if get_depth(urlparse(u).path) >= 4]

    # Extract top-level directories
    top_dirs = Counter()
    for p in paths:
        parts = p.strip("/").split("/")
        if parts and parts[0]:
            top_dirs[parts[0]] += 1

    return {
        "total_urls": len(urls),
        "depth_distribution": dict(sorted(depth_counter.items())),
        "top_directories": dict(top_dirs.most_common(15)),
        "dynamic_urls": dynamic_urls,
        "deep_pages": deep_urls,
        "duplicate_slug_candidates": duplicate_slugs,
        "top_url_patterns": [{"pattern": p, "count": c} for p, c in top_patterns],
    }
def grade_depth_distribution(dist: dict) -> str:
    deep = sum(v for k, v in dist.items() if k >= 4)
    total = sum(dist.values())
    if total == 0:
        return "N/A"
    pct = deep / total * 100
    if pct < 5:
        return "🟢 Excellent"
    if pct < 15:
        return "🟡 Acceptable"
    return "🔴 Too many deep pages"

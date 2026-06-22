# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sitemap_analyzer_base import *  # noqa: F403,E402
# fmt: off
from sitemap_analyzer_p1 import SAMPLE_SITEMAP  # noqa: E402,E501
from sitemap_analyzer_p2 import analyze_urls, grade_depth_distribution, parse_sitemap  # noqa: E402,E501
# fmt: on


def print_report(analysis: dict) -> None:
    print("\n" + "═" * 62)
    print("  SITEMAP STRUCTURE ANALYSIS")
    print("═" * 62)
    print(f"\n  Total URLs: {analysis['total_urls']}")

    print("\n── Depth Distribution ──")
    dist = analysis["depth_distribution"]
    total = analysis["total_urls"]
    for depth, count in sorted(dist.items()):
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        label = "homepage" if depth == 0 else f"{'  ' * min(depth, 3)}/{'…/' * (depth - 1)}page"
        print(f"   Depth {depth}: {count:4d} pages ({pct:5.1f}%)  {bar}  {label}")

    print(f"\n   Rating: {grade_depth_distribution(dist)}")
    deep_pct = sum(v for k, v in dist.items() if k >= 4) / total * 100 if total else 0
    if deep_pct >= 5:
        print("   ⚠️  More than 5% of pages are 4+ levels deep.")
        print("      Consider flattening structure or adding shortcut links.")

    print("\n── Top-Level Directories ──")
    for d, count in analysis["top_directories"].items():
        pct = count / total * 100 if total else 0
        print(f"   /{d:<30s}  {count:4d} URLs ({pct:.1f}%)")

    print("\n── URL Pattern Analysis ──")
    for p in analysis["top_url_patterns"]:
        print(f"   {p['pattern']:<45s}  {p['count']:4d} URLs")

    if analysis["dynamic_urls"]:
        print(f"\n── Dynamic URLs Detected ({len(analysis['dynamic_urls'])}) ──")
        print("   ⚠️  URLs with query parameters should usually be excluded from sitemap.")
        print("      Use canonical tags or robots.txt to prevent duplicate content indexing.")
        for u in analysis["dynamic_urls"][:5]:
            print(f"   {u}")
        if len(analysis["dynamic_urls"]) > 5:
            print(f"   ... and {len(analysis['dynamic_urls']) - 5} more")

    if analysis["deep_pages"]:
        print(f"\n── Deep Pages (4+ Levels) ({len(analysis['deep_pages'])}) ──")
        print("   ⚠️  Pages this deep may have weak crawl equity. Add internal shortcuts.")
        for url, depth in analysis["deep_pages"][:5]:
            print(f"   Depth {depth}: {url}")
        if len(analysis["deep_pages"]) > 5:
            print(f"   ... and {len(analysis['deep_pages']) - 5} more")

    if analysis["duplicate_slug_candidates"]:
        print(f"\n── Potential Duplicate Path Issues ({len(analysis['duplicate_slug_candidates'])}) ──")
        print("   ⚠️  Same slug appears in multiple directories — possible duplicate content.")
        for item in analysis["duplicate_slug_candidates"][:5]:
            print(f"   Slug: '{item['slug']}'")
            for u in item["urls"]:
                print(f"     - {u}")
        if len(analysis["duplicate_slug_candidates"]) > 5:
            print(f"   ... and {len(analysis['duplicate_slug_candidates']) - 5} more")

    print("\n── Recommendations ──")
    has_issues = False
    if analysis["dynamic_urls"]:
        print("   1. Remove dynamic URLs (with ?) from sitemap.")
        has_issues = True
    if analysis["deep_pages"]:
        print(f"   {'2' if has_issues else '1'}. Flatten deep URL structures or add internal shortcut links.")
        has_issues = True
    if analysis["duplicate_slug_candidates"]:
        print(f"   {'3' if has_issues else '1'}. Review duplicate slug paths — consolidate or add canonical tags.")
        has_issues = True
    if not has_issues:
        print("   ✅ No major structural issues detected in this sitemap.")

    print("\n" + "═" * 62)
def load_content(source: str) -> str:
    """Load sitemap from file path, URL, or stdin."""
    if source.startswith("http://") or source.startswith("https://"):
        try:
            with urllib.request.urlopen(source, timeout=10) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"Error fetching URL: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {source}", file=sys.stderr)
            sys.exit(1)
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyzes sitemap.xml files for structure, depth, and potential issues. "
                    "Reports depth distribution, URL patterns, orphan candidates, and duplicates."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a sitemap.xml file or URL (https://...). "
             "Use '-' to read from stdin. If omitted, runs embedded sample."
    )
    args = parser.parse_args()

    if args.file:
        if args.file == "-":
            content = sys.stdin.read()
        else:
            content = load_content(args.file)
    else:
        print("No file or URL provided — running on embedded sample sitemap.\n")
        content = SAMPLE_SITEMAP

    urls = parse_sitemap(content)
    if not urls:
        print("No URLs found in sitemap.", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_urls(urls)
    print_report(analysis)

    # JSON output
    print("\n── JSON Summary ──")
    summary = {
        "total_urls": analysis["total_urls"],
        "depth_distribution": analysis["depth_distribution"],
        "dynamic_url_count": len(analysis["dynamic_urls"]),
        "deep_page_count": len(analysis["deep_pages"]),
        "duplicate_slug_count": len(analysis["duplicate_slug_candidates"]),
        "top_directories": analysis["top_directories"],
    }
    print(json.dumps(summary, indent=2))

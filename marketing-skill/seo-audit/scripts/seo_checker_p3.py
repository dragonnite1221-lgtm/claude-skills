# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_checker_base import *  # noqa: F403,E402
# fmt: off
from seo_checker_p2 import analyze_html  # noqa: E402,E501
# fmt: on


def compute_overall_score(results: dict) -> int:
    weights = {
        "title": 20,
        "meta_description": 15,
        "h1": 15,
        "heading_hierarchy": 10,
        "image_alt_text": 10,
        "link_ratio": 10,
        "word_count": 15,
        "viewport_meta": 5,
    }
    total_w = sum(weights.values())
    score = sum(results[k]["score"] * w for k, w in weights.items() if k in results)
    return round(score / total_w)
DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>10 Ways to Boost Your Marketing ROI in 2024</title>
  <meta name="description" content="Discover ten proven strategies to maximize your marketing return on investment, reduce wasted ad spend, and grow revenue faster with data-driven techniques.">
</head>
<body>
  <h1>10 Ways to Boost Your Marketing ROI in 2024</h1>
  <p>Marketing budgets are tight. Every dollar counts. Here is how to make yours work harder.</p>
  <h2>1. Audit Your Current Spend</h2>
  <p>Before adding channels, understand where money goes. Most companies waste 30% of budget on low-ROI tactics.</p>
  <img src="audit-chart.png" alt="Marketing spend audit chart showing channel breakdown">
  <h2>2. Double Down on SEO</h2>
  <p>Organic traffic compounds. Paid stops the moment you stop spending. Invest in content that ranks.</p>
  <img src="seo-graph.png" alt="SEO traffic growth over 12 months">
  <h3>On-Page Optimization</h3>
  <p>Start with title tags, meta descriptions, and heading structure before anything else.</p>
  <h2>3. Improve Email Open Rates</h2>
  <p>Subject lines determine 80% of open rates. Test at least three variants per campaign.</p>
  <a href="/email-templates">Email templates library</a>
  <a href="https://mailchimp.com">Mailchimp</a>
  <h2>4. Use Retargeting Wisely</h2>
  <p>Retargeting works best with frequency caps. Show the same ad more than 7 times and you hurt brand perception.</p>
  <h2>5. Build Landing Pages That Convert</h2>
  <p>A single focused landing page beats a homepage for paid traffic every time. Remove navigation. Add a clear CTA.</p>
  <a href="/landing-page-guide">Landing page guide</a>
  <a href="/cro-checklist">CRO checklist</a>
  <a href="https://unbounce.com">Unbounce</a>
  <p>With these strategies you should see measurable improvement within 90 days. Start with the audit — it reveals the quickest wins.</p>
</body>
</html>"""
def main():
    parser = argparse.ArgumentParser(
        description="On-page SEO checker — scores an HTML page 0-100."
    )
    parser.add_argument("--file", help="Path to HTML file")
    parser.add_argument("--url", help="URL to fetch and analyze")
    parser.add_argument("--domain", default="", help="Base domain for internal link detection")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    elif args.url:
        with urllib.request.urlopen(args.url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    else:
        html = DEMO_HTML
        if not args.json:
            print("No input provided — running in demo mode.\n")

    results = analyze_html(html, base_domain=args.domain)
    overall = compute_overall_score(results)

    if args.json:
        output = {"overall_score": overall, "checks": results}
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    ICONS = {True: "✅", False: "❌"}
    print("=" * 60)
    print(f"  SEO AUDIT RESULTS   Overall Score: {overall}/100")
    print("=" * 60)

    checks = [
        ("Title Tag",           "title"),
        ("Meta Description",    "meta_description"),
        ("H1 Tag",              "h1"),
        ("Heading Hierarchy",   "heading_hierarchy"),
        ("Image Alt Text",      "image_alt_text"),
        ("Link Ratio",          "link_ratio"),
        ("Word Count",          "word_count"),
        ("Viewport Meta",       "viewport_meta"),
    ]

    for label, key in checks:
        r = results[key]
        icon = ICONS[r["pass"]]
        score = r["score"]
        note = r["note"]
        print(f"  {icon}  {label:<22} [{score:>3}/100]  {note}")

    print("=" * 60)

    # Grade
    grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D" if overall >= 40 else "F"
    print(f"  Grade: {grade}   Score: {overall}/100")
    print("=" * 60)

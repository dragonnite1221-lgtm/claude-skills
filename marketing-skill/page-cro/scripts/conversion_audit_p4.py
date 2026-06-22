# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from conversion_audit_base import *  # noqa: F403,E402
# fmt: off
from conversion_audit_p3 import audit  # noqa: E402,E501
# fmt: on


DEMO_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Get Your Free Marketing Audit</title>
</head>
<body>
  <header>
    <img src="logo.png" alt="Acme Corp logo" class="logo">
    <a href="#form" class="btn cta">Get Free Audit</a>
  </header>
  <section class="hero">
    <h1>Stop Wasting Your Ad Budget</h1>
    <p>Join 12,400 marketers who cut wasted spend by 35% in 30 days.</p>
    <button>Start Free Trial</button>
  </section>
  <section class="social-proof">
    <h2>What Our Customers Say</h2>
    <blockquote>"This tool saved us $50,000 in the first quarter." — Sarah M., CMO</blockquote>
    <blockquote>"Best investment we made in 2023." — James T., Head of Growth</blockquote>
    <p>Rated 4.9/5 on G2 with 2,400+ reviews</p>
    <p>Trusted by 500+ companies worldwide</p>
    <img src="google-partner.png" alt="Google Partner badge" class="badge">
    <img src="trustpilot.png" alt="Trustpilot certified" class="badge">
  </section>
  <section id="form">
    <h2>Get Your Free Audit</h2>
    <form>
      <input type="text" name="name" placeholder="Your name">
      <input type="email" name="email" placeholder="Work email">
      <button type="submit">Get My Free Audit</button>
    </form>
    <p>🔒 SSL secured. We never share your data. Unsubscribe anytime.</p>
    <p>30-day money-back guarantee. No risk.</p>
  </section>
</body>
</html>"""
def main():
    parser = argparse.ArgumentParser(
        description="CRO audit — analyzes an HTML page for conversion signals."
    )
    parser.add_argument("--file", help="Path to HTML file")
    parser.add_argument("--url", help="URL to fetch and analyze")
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

    result = audit(html)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    cats = result["categories"]
    overall = result["overall_score"]

    print("=" * 62)
    print(f"  CRO AUDIT RESULTS   Overall Score: {overall}/100")
    print("=" * 62)

    rows = [
        ("CTA Buttons",     "cta_buttons"),
        ("Social Proof",    "social_proof"),
        ("Trust Signals",   "trust_signals"),
        ("Forms",           "forms"),
        ("Mobile Viewport", "viewport_mobile"),
    ]

    for label, key in rows:
        c = cats[key]
        score = c["score"]
        weight = c["weight"]
        bar_len = round(score / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        icon = "✅" if score >= 70 else ("⚠️ " if score >= 40 else "❌")
        print(f"  {icon} {label:<18} [{bar}] {score:>3}/100  (weight {weight})")

    print()
    # Detail callouts
    cta = cats["cta_buttons"]
    print(f"  CTAs: {cta['button_count']} buttons, {cta['cta_link_count']} CTA links, "
          f"{cta['cta_text_count']} CTA text phrases, {cta['above_fold_ctas']} above fold")

    sp = cats["social_proof"]
    print(f"  Social Proof: {sp['testimonial_signals']} testimonial signals, "
          f"{sp['logo_badge_images']} logos/badges")

    ts = cats["trust_signals"]
    print(f"  Trust: SSL({ts['ssl_mentions']}) Guarantee({ts['guarantee_mentions']}) "
          f"Privacy({ts['privacy_mentions']})")

    fm = cats["forms"]
    print(f"  Forms: {fm['form_count']} form(s), {fm['field_count']} field(s) — {fm['note']}")

    print()
    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"
    print("=" * 62)
    print(f"  Grade: {grade}   Score: {overall}/100")
    print("=" * 62)

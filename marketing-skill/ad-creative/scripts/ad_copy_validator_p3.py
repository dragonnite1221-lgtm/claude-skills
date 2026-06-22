# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_copy_validator_base import *  # noqa: F403,E402
# fmt: off
from ad_copy_validator_p1 import PLATFORM_SPECS, check_all_caps, check_excessive_punctuation, check_prohibited_phrases, check_trademark_mentions, count_chars, score_ad  # noqa: E402,E501
from ad_copy_validator_p2 import validate_google_rsa, validate_linkedin, validate_meta_feed  # noqa: E402,E501
# fmt: on


def validate_generic(ad, platform_key):
    spec = PLATFORM_SPECS.get(platform_key, {})
    issues = defaultdict(list)
    report = []

    text = ad.get("primary_text", ad.get("text", ""))
    max_chars = spec.get("primary_text_max", 280)

    if text:
        length = count_chars(text)
        status = "✅" if length <= max_chars else "❌"
        if length > max_chars:
            issues["char_over_limit"].append(f"Text {length} chars (max {max_chars})")
        report.append(f"  Text: {status} ({length}/{max_chars} chars)")

        for check_fn, key in [
            (check_all_caps, "all_caps"),
            (check_excessive_punctuation, "excessive_punctuation"),
            (check_trademark_mentions, "trademark_mention"),
            (check_prohibited_phrases, "prohibited_phrase"),
        ]:
            result = check_fn(text)
            if result:
                issues[key].extend(result if isinstance(result, list) else [str(result)])

    return report, dict(issues)
def validate_ad(ad):
    platform = ad.get("platform", "").lower()

    if platform == "google_rsa":
        return validate_google_rsa(ad)
    elif platform == "meta_feed":
        return validate_meta_feed(ad)
    elif platform == "linkedin":
        return validate_linkedin(ad)
    elif platform in ("twitter", "tiktok"):
        return validate_generic(ad, platform)
    else:
        return [f"  ⚠️  Unknown platform '{platform}' — using generic validation"], {}
def format_report(ad, char_lines, issues):
    platform = ad.get("platform", "unknown")
    spec = PLATFORM_SPECS.get(platform, {})
    platform_name = spec.get("name", platform.upper())

    score = score_ad(issues)
    grade = "🟢 Excellent" if score >= 85 else "🟡 Needs Work" if score >= 60 else "🔴 High Risk"

    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Platform: {platform_name}")
    lines.append(f"Quality Score: {score}/100  {grade}")
    lines.append(f"{'='*60}")

    lines.append("\nCharacter Counts:")
    lines.extend(char_lines)

    if issues:
        lines.append("\nIssues Found:")
        category_labels = {
            "char_over_limit": "❌ Over character limit",
            "all_caps": "⚠️  ALL CAPS words",
            "excessive_punctuation": "⚠️  Excessive punctuation",
            "trademark_mention": "🚫 Trademarked term",
            "prohibited_phrase": "🚫 Prohibited phrase",
            "suspicious_claim": "🚨 Suspicious claim (review required)",
            "count_too_few": "⚠️  Too few elements",
            "count_too_many": "⚠️  Too many elements",
        }
        for category, items in issues.items():
            label = category_labels.get(category, category)
            lines.append(f"  {label}: {', '.join(str(i) for i in items)}")
    else:
        lines.append("\n✅ No rejection triggers found.")

    lines.append("")
    return "\n".join(lines)
SAMPLE_ADS = [
    {
        "platform": "google_rsa",
        "headlines": [
            "Cut Reporting Time by 80%",                   # 26 chars ✅
            "Automated Reports, Zero Effort",              # 31 chars ❌ over limit
            "Your Data. Your Way. Every Week.",            # 33 chars ❌ over limit
            "Save 8 Hours Per Week on Reports",            # 32 chars ❌ over limit
            "Try Free for 14 Days",                        # 21 chars ✅
            "No Code. No Complexity. Just Results.",        # 38 chars ❌
            "5,000 Teams Use This",                        # 21 chars ✅
            "Replace Your Weekly Standup Deck",            # 32 chars ❌
            "Connect Your Tools in 15 Minutes",            # 32 chars ❌
            "Instant Dashboards for Your Team",            # 32 chars ❌
            "Start Free — No Credit Card",                 # 28 chars ✅
            "Built for Growth Teams",                      # 22 chars ✅
            "See Your KPIs at a Glance",                   # 25 chars ✅
            "Data-Driven Decisions, Made Easy",            # 32 chars ❌
            "GUARANTEED Results — Try Now!!!",             # 31 chars ❌ + ALL CAPS + excessive punct
        ],
        "descriptions": [
            "Connect your tools, set your KPIs, and let the platform handle the weekly reporting. Free 14-day trial.",  # 103 chars ❌
            "Stop wasting Monday mornings on spreadsheets. Automated reports your whole team actually reads.",           # 94 chars ❌
        ],
    },
    {
        "platform": "meta_feed",
        "primary_text": "Your team is shipping features, but nobody can see the impact. [Product] connects your tools and shows you exactly what's working — in one dashboard, updated automatically. Start free today.",
        "headline": "See Your Impact, Automatically",
    },
    {
        "platform": "linkedin",
        "intro_text": "Growth teams at 3,200+ companies use [Product] to replace their manual weekly reports with automated dashboards.",
        "headline": "Automated Reporting for Growth Teams",
    },
    {
        "platform": "twitter",
        "primary_text": "Stop spending 8 hours on a report nobody reads. [Product] automates it — connect your tools, set your KPIs, and it runs itself. Free trial → [link]",
    },
]

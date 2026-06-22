# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from profile_auditor_base import *  # noqa: F403,E402
# fmt: off
from profile_auditor_p1 import AuditReport, ProfileData, audit_bio  # noqa: E402,E501
from profile_auditor_p2 import audit_activity, calculate_score, generate_recommendations  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Audit an X/Twitter profile for growth readiness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --handle @rezarezvani --bio "CTO building AI products" --followers 5000
  %(prog)s --bio "Entrepreneur | Dreamer | Hustle" --followers 200 --posts-per-week 3
  %(prog)s --handle @example --followers 50000 --posts-per-week 21 --reply-ratio 0.4 --json
        """)

    parser.add_argument("--handle", default="@unknown", help="X handle")
    parser.add_argument("--bio", default="", help="Current bio text")
    parser.add_argument("--followers", type=int, default=0, help="Follower count")
    parser.add_argument("--following", type=int, default=0, help="Following count")
    parser.add_argument("--posts-per-week", type=float, default=0, help="Average posts per week")
    parser.add_argument("--reply-ratio", type=float, default=0, help="Fraction of posts that are replies (0-1)")
    parser.add_argument("--has-pinned", action="store_true", help="Has a pinned tweet")
    parser.add_argument("--pinned-age-days", type=int, default=0, help="Age of pinned tweet in days")
    parser.add_argument("--has-link", action="store_true", help="Has link in profile")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    profile = ProfileData(
        handle=args.handle,
        bio=args.bio,
        followers=args.followers,
        following=args.following,
        posts_per_week=args.posts_per_week,
        reply_ratio=args.reply_ratio,
        has_pinned=args.has_pinned,
        pinned_age_days=args.pinned_age_days,
        has_link=args.has_link,
    )

    findings = audit_bio(profile) + audit_activity(profile)
    score, grade = calculate_score(findings)
    recs = generate_recommendations(findings, profile)

    report = AuditReport(
        handle=profile.handle,
        score=score,
        grade=grade,
        findings=[asdict(f) for f in findings],
        recommendations=recs,
    )

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  X PROFILE AUDIT — {report.handle}")
        print(f"{'='*60}")
        print(f"\n  Score: {report.score}/100 (Grade: {report.grade})\n")

        for f in findings:
            icon = {"GOOD": "✅", "WARN": "⚠️", "CRITICAL": "🔴"}.get(f.status, "❓")
            print(f"  {icon} [{f.area}] {f.message}")
            if f.fix and f.status != "GOOD":
                print(f"     → {f.fix}")

        if recs:
            print(f"\n  {'─'*56}")
            print(f"  TOP RECOMMENDATIONS\n")
            for i, r in enumerate(recs, 1):
                print(f"  {i}. {r}")

        print(f"\n{'='*60}\n")

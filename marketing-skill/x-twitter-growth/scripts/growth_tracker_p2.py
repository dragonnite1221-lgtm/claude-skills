# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from growth_tracker_base import *  # noqa: F403,E402
# fmt: off
from growth_tracker_p1 import generate_report, get_data_file, load_snapshots, project_milestone, record_snapshot  # noqa: E402,E501
# fmt: on


def print_report(report: dict):
    print(f"\n{'='*60}")
    print(f"  GROWTH REPORT — {report['handle']}")
    print(f"{'='*60}")

    if "error" in report:
        print(f"\n  ⚠️  {report['error']}")
        print(f"  Record data first: python3 growth_tracker.py --record --handle {report['handle']} --followers N")
        print()
        return

    print(f"\n  Current followers:    {report['current_followers']:,}")
    print(f"  Data points:         {report['data_points']}")
    print(f"  Tracking since:      {report['first_record'][:10]}")

    if "follower_change" in report:
        change_icon = "📈" if report["follower_change"] > 0 else "📉" if report["follower_change"] < 0 else "➡️"
        print(f"\n  {change_icon} Change:  {report['follower_change']:+,} followers over {report['days_tracked']} days")
        print(f"  Daily avg:           {report.get('daily_growth', 0):+.1f}/day")
        print(f"  Weekly avg:          {report.get('weekly_growth', 0):+.1f}/week")
        print(f"  30-day projection:   {report.get('monthly_projection', 0):+,}")

        if "growth_percent" in report:
            print(f"  Growth rate:         {report['growth_percent']:+.1f}%")

        if "engagement_trend" in report:
            trend_icon = "📈" if report["engagement_trend"] == "improving" else "📉"
            print(f"  Engagement:          {trend_icon} {report['engagement_trend']} (avg {report['avg_engagement_rate']}%)")

    print(f"\n{'='*60}\n")
def main():
    parser = argparse.ArgumentParser(
        description="Track X/Twitter account growth over time",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--record", action="store_true", help="Record a new snapshot")
    parser.add_argument("--report", action="store_true", help="Generate growth report")
    parser.add_argument("--milestone", action="store_true", help="Project when target will be reached")

    parser.add_argument("--handle", required=True, help="X handle")
    parser.add_argument("--followers", type=int, default=0, help="Current follower count")
    parser.add_argument("--following", type=int, default=0, help="Current following count")
    parser.add_argument("--eng-rate", type=float, default=0, help="Current engagement rate (pct)")
    parser.add_argument("--posts-week", type=float, default=0, help="Posts per week")
    parser.add_argument("--notes", default="", help="Notes for this snapshot")
    parser.add_argument("--period", default="all", help="Report period: 7d, 30d, 90d, all")
    parser.add_argument("--target", type=int, default=0, help="Follower milestone target")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if not args.handle.startswith("@"):
        args.handle = f"@{args.handle}"

    if args.record:
        if args.followers <= 0:
            print("Error: --followers required for recording", file=sys.stderr)
            sys.exit(1)
        entry = record_snapshot(args.handle, args.followers, args.following,
                                args.eng_rate, args.posts_week, args.notes)
        if args.json:
            print(json.dumps(entry, indent=2))
        else:
            print(f"  ✅ Recorded: {args.handle} — {args.followers:,} followers")
            print(f"     File: {get_data_file(args.handle)}")

    elif args.report:
        period_days = 0
        if args.period != "all":
            period_days = int(args.period.rstrip("d"))
        entries = load_snapshots(args.handle, period_days)
        report = generate_report(args.handle, entries)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report)

    elif args.milestone:
        if args.target <= 0:
            print("Error: --target required for milestone projection", file=sys.stderr)
            sys.exit(1)
        entries = load_snapshots(args.handle)
        result = project_milestone(args.handle, entries, args.target)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"  ⚠️  {result['error']}")
            elif "status" in result and "days_needed" not in result:
                print(f"  🎉 {result['status']}")
            else:
                print(f"\n  🎯 Milestone Projection: {result['handle']}")
                print(f"  Current:  {result['current']:,}")
                print(f"  Target:   {result['target']:,}")
                print(f"  Gap:      {result['remaining']:,}")
                print(f"  Growth:   {result['daily_growth']:+.1f}/day")
                print(f"  ETA:      {result['projected_date']} (~{result['days_needed']} days)")
                print()

    else:
        parser.print_help()

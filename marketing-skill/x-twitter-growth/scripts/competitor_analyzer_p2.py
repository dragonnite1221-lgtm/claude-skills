# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402
# fmt: off
from competitor_analyzer_p1 import CompetitorProfile, analyze_competitors, calculate_engagement_rate  # noqa: E402,E501
# fmt: on


def print_report(competitors: list, insights: list):
    print(f"\n{'='*70}")
    print(f"  COMPETITIVE ANALYSIS REPORT")
    print(f"{'='*70}")

    # Profile summary table
    print(f"\n  {'Handle':<20} {'Followers':>10} {'Posts/wk':>10} {'Eng Rate':>10}")
    print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*10}")
    for c in competitors:
        er = calculate_engagement_rate(c)
        print(f"  {c.handle:<20} {c.followers:>10,} {c.posts_per_week:>10.0f} {er:>9.2f}%")

    # Insights
    if insights:
        print(f"\n  {'─'*66}")
        print(f"  KEY INSIGHTS\n")

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_insights = sorted(insights, key=lambda x: priority_order.get(x.priority, 3))

        for i in sorted_insights:
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪"}.get(i.priority, "❓")
            print(f"  {icon} [{i.category}] {i.finding}")
            print(f"     → {i.opportunity}")
            print()

    # Action items
    print(f"  {'─'*66}")
    print(f"  NEXT STEPS\n")
    print(f"  1. Search each competitor's profile on X — note their pinned tweet and bio")
    print(f"  2. Read their last 20 posts — categorize by format and topic")
    print(f"  3. Identify their top 3 performing posts — what made them work?")
    print(f"  4. Find gaps — what topics do they NOT cover that you can own?")
    print(f"  5. Set engagement targets based on their metrics as benchmarks")
    print(f"\n{'='*70}\n")
def main():
    parser = argparse.ArgumentParser(
        description="Analyze X/Twitter competitors for content strategy insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --handles @user1 @user2
  %(prog)s --import competitors.json
  
  JSON format for --import:
  [{"handle": "@user1", "followers": 50000, "posts_per_week": 14, ...}]
        """)

    parser.add_argument("--handles", nargs="+", default=[], help="Competitor handles")
    parser.add_argument("--import", dest="import_file", help="Import from JSON file")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    competitors = []

    if args.import_file:
        with open(args.import_file) as f:
            data = json.load(f)
            for item in data:
                competitors.append(CompetitorProfile(**item))
    elif args.handles:
        for handle in args.handles:
            if not handle.startswith("@"):
                handle = f"@{handle}"
            competitors.append(CompetitorProfile(handle=handle))

        if all(c.followers == 0 for c in competitors):
            print(f"\n  ℹ️  Handles registered: {', '.join(c.handle for c in competitors)}")
            print(f"  To get full analysis, provide data via JSON import:")
            print(f"  1. Research each profile on X")
            print(f"  2. Create a JSON file with follower counts, posting frequency, etc.")
            print(f"  3. Run: {sys.argv[0]} --import data.json")
            print(f"\n  Example JSON:")
            example = [asdict(CompetitorProfile(
                handle="@example",
                followers=25000,
                following=1200,
                posts_per_week=14,
                avg_likes=150,
                avg_replies=30,
                avg_retweets=20,
                thread_frequency="weekly",
                top_topics=["AI", "startups", "engineering"],
            ))]
            print(f"  {json.dumps(example, indent=2)}")
            print()
            return

    if not competitors:
        print("Error: provide --handles or --import", file=sys.stderr)
        sys.exit(1)

    insights = analyze_competitors(competitors)

    if args.json:
        print(json.dumps({
            "competitors": [asdict(c) for c in competitors],
            "insights": [asdict(i) for i in insights],
        }, indent=2))
    else:
        print_report(competitors, insights)

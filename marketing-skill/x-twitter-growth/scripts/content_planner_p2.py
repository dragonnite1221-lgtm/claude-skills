# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_planner_base import *  # noqa: F403,E402
# fmt: off
from content_planner_p1 import generate_plan  # noqa: E402,E501
# fmt: on


def print_plan(plans: list, niche: str):
    print(f"\n{'='*70}")
    print(f"  X/TWITTER CONTENT PLAN — {niche.upper()}")
    print(f"{'='*70}")

    for week in plans:
        print(f"\n  WEEK {week['week_number']} ({week['start_date']} to {week['end_date']})")
        print(f"  Theme: {week['focus_theme']}")
        print(f"  Posts: {week['total_posts']} | Threads: {week['thread_count']}")
        print(f"  {'─'*66}")

        for day in week['days']:
            print(f"\n  {day['day_of_week']:9} {day['date']}")
            for post in day['posts']:
                fmt_icon = {
                    "thread": "🧵",
                    "atomic_tweet": "💬",
                    "question": "❓",
                    "quote_tweet": "🔄",
                    "reply_session": "💬",
                }.get(post['format'], "📝")

                print(f"    {fmt_icon} {post['time']:12} [{post['format']:<14}] {post['topic_angle']}")
                if post['notes']:
                    print(f"       ℹ️  {post['notes']}")

            print(f"    📊 Engagement: {day['engagement_target']}")

    print(f"\n{'='*70}")
    print(f"  WEEKLY TARGETS")
    print(f"  • Reply to 10+ accounts in your niche daily")
    print(f"  • Quote tweet 2-3 relevant posts per week")
    print(f"  • Update pinned tweet if a thread outperforms current pin")
    print(f"  • Review analytics every Sunday — double down on what works")
    print(f"{'='*70}\n")
def main():
    parser = argparse.ArgumentParser(
        description="Generate X/Twitter content calendars",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--niche", required=True, help="Your content niche")
    parser.add_argument("--frequency", type=int, default=3, help="Posts per day (default: 3)")
    parser.add_argument("--weeks", type=int, default=2, help="Weeks to plan (default: 2)")
    parser.add_argument("--start", default="", help="Start date YYYY-MM-DD (default: next Monday)")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.start:
        start = datetime.strptime(args.start, "%Y-%m-%d")
    else:
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start = today + timedelta(days=days_until_monday)

    plans = generate_plan(args.niche, args.frequency, args.weeks, start)

    if args.json:
        print(json.dumps(plans, indent=2))
    else:
        print_plan(plans, args.niche)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from social_calendar_generator_base import *  # noqa: F403,E402


def build_markdown(result: dict) -> str:
    m = result["meta"]
    lines = []
    lines.append(f"# Social Media Content Calendar")
    lines.append(f"**Period:** {m['start_date']} → {m['end_date']}  "
                 f"| **{m['weeks']} weeks** | **{m['total_posts']} total posts**\n")

    # Per-platform distribution
    for pname, pc in result["platforms"].items():
        lines.append(f"## {pname}  ({pc['total_posts']} posts)\n")
        lines.append("**Pillar distribution:**")
        for pillar, count in pc["pillar_distribution"].items():
            pct = pc["pillar_pct"][pillar]
            lines.append(f"- {pillar}: {count} posts ({pct}%)")
        lines.append("")

    # Weekly calendar tables
    for week_num in range(1, m["weeks"] + 1):
        lines.append(f"## Week {week_num}\n")
        header = "| Date | Day | " + " | ".join(m["platforms"]) + " |"
        sep    = "|---|---|" + "|".join(["---"] * len(m["platforms"])) + "|"
        lines.append(header)
        lines.append(sep)

        # Group by date
        week_posts = defaultdict(dict)
        for post in result["timeline"]:
            if post["week_number"] == week_num:
                week_posts[post["date"]][post["platform"]] = post

        for day_date in sorted(week_posts.keys()):
            day_posts = week_posts[day_date]
            weekday   = list(day_posts.values())[0]["weekday"] if day_posts else ""
            cells     = []
            for pname in m["platforms"]:
                if pname in day_posts:
                    p    = day_posts[pname]
                    cell = f"{p['pillar_emoji']} **{p['pillar']}**<br/>{p['content_type']}"
                else:
                    cell = "—"
                cells.append(cell)
            lines.append(f"| {day_date} | {weekday} | " + " | ".join(cells) + " |")

        lines.append("")

    # Legend
    lines.append("## Content Pillars\n")
    for pc in result["platforms"].values():
        break
    from_meta = result["meta"]["pillars"]
    lines.append("| Pillar | Description |")
    lines.append("|---|---|")
    for pname, pc in result["platforms"].items():
        # Get pillar descriptions from first platform's posts
        pillar_desc = {}
        for post in pc["posts"]:
            pillar_desc[post["pillar"]] = post["description"]
        for pillar in from_meta:
            desc = pillar_desc.get(pillar, "")
            lines.append(f"| {pillar} | {desc} |")
        break

    lines.append("")
    return "\n".join(lines)
def pretty_print(result: dict) -> None:
    m = result["meta"]
    print("\n" + "=" * 70)
    print("  📅  SOCIAL MEDIA CONTENT CALENDAR GENERATOR")
    print("=" * 70)
    print(f"\n  Period     : {m['start_date']} → {m['end_date']}  ({m['weeks']} weeks)")
    print(f"  Platforms  : {', '.join(m['platforms'])}")
    print(f"  Total posts: {m['total_posts']}")
    print(f"  Pillars    : {', '.join(m['pillars'])}")

    for pname, pc in result["platforms"].items():
        print(f"\n  {'─'*60}")
        print(f"  📣  {pname.upper()}  — {pc['total_posts']} posts  "
              f"({pc['posts_per_week']}/week)")
        print(f"  Best days: {', '.join(pc['best_days'])}")
        print(f"  Pillar distribution:")
        for pillar, count in pc["pillar_distribution"].items():
            pct = pc["pillar_pct"][pillar]
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"    {pillar:<16}  {count:>3} posts  {pct:>3}%  {bar}")

    print(f"\n  {'─'*70}")
    print(f"  📆  WEEKLY SCHEDULE\n")

    # Group timeline by week
    from collections import defaultdict
    weeks_data = defaultdict(list)
    for post in result["timeline"]:
        weeks_data[post["week_number"]].append(post)

    for week_num in sorted(weeks_data.keys()):
        print(f"  WEEK {week_num}")
        print(f"  {'Date':<12} {'Day':<11}" +
              "".join(f" {p:<22}" for p in m["platforms"]))
        print("  " + "─" * (12 + 11 + 23 * len(m["platforms"])))

        # Group by date
        day_map = defaultdict(dict)
        for post in weeks_data[week_num]:
            day_map[post["date"]][post["platform"]] = post

        for day_date in sorted(day_map.keys()):
            dp      = day_map[day_date]
            weekday = list(dp.values())[0]["weekday"]
            row     = f"  {day_date:<12} {weekday:<11}"
            for pname in m["platforms"]:
                if pname in dp:
                    p    = dp[pname]
                    cell = f"{p['pillar_emoji']} {p['pillar'][:10]}/{p['content_type'][:8]}"
                else:
                    cell = "—"
                row += f" {cell:<22}"
            print(row)
        print()

    print("  💡  TIP: Re-run with --markdown to export a copyable Markdown table.\n")

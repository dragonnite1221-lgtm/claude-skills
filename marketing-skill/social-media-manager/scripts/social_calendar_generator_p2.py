# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from social_calendar_generator_base import *  # noqa: F403,E402
# fmt: off
from social_calendar_generator_p1 import CONTENT_TYPE_HINTS, DEMO_CONFIG, WEEKDAY_NAMES, build_pillar_sequence, next_monday, parse_date  # noqa: E402,E501
# fmt: on


def build_calendar(config: dict) -> dict:
    pillars   = config.get("pillars", DEMO_CONFIG["pillars"])
    platforms = config.get("platforms", DEMO_CONFIG["platforms"])
    weeks     = config.get("weeks", 4)

    start_raw = config.get("start_date")
    if start_raw:
        start = parse_date(start_raw)
    else:
        start = next_monday()

    pillar_map = {p["name"]: p for p in pillars}

    # Pre-compute total posts per platform
    calendar_by_platform = {}

    for platform in platforms:
        pname     = platform["name"]
        ppw       = platform.get("posts_per_week", 3)
        best_days = platform.get("best_days", WEEKDAY_NAMES[:5])

        # Generate post dates across the period
        post_dates = []
        for week in range(weeks):
            week_start = start + timedelta(weeks=week)
            day_count  = 0
            for day_offset in range(7):
                if day_count >= ppw:
                    break
                d      = week_start + timedelta(days=day_offset)
                d_name = WEEKDAY_NAMES[d.weekday()]
                if d_name in best_days:
                    post_dates.append(d)
                    day_count += 1

        total_posts = len(post_dates)
        pillar_seq  = build_pillar_sequence(pillars, total_posts)

        posts = []
        for i, (post_date, pillar_name) in enumerate(zip(post_dates, pillar_seq)):
            pillar  = pillar_map[pillar_name]
            hints   = CONTENT_TYPE_HINTS.get(pillar_name, ["Post"])
            ct_hint = hints[i % len(hints)]
            posts.append({
                "date":         post_date.isoformat(),
                "weekday":      WEEKDAY_NAMES[post_date.weekday()],
                "week_number":  (post_date - start).days // 7 + 1,
                "platform":     pname,
                "pillar":       pillar_name,
                "pillar_emoji": pillar.get("emoji", ""),
                "description":  pillar.get("description", ""),
                "content_type": ct_hint,
                "content_type_hint": platform.get("content_type_hint", ""),
            })

        # Pillar distribution stats
        dist = defaultdict(int)
        for p in posts:
            dist[p["pillar"]] += 1
        dist_pct = {k: round(v / total_posts * 100) for k, v in dist.items()}

        calendar_by_platform[pname] = {
            "platform":            pname,
            "posts_per_week":      ppw,
            "total_weeks":         weeks,
            "total_posts":         total_posts,
            "best_days":           best_days,
            "posts":               posts,
            "pillar_distribution": dict(dist),
            "pillar_pct":          dist_pct,
        }

    # Global summary
    all_posts = []
    for pc in calendar_by_platform.values():
        all_posts.extend(pc["posts"])
    all_posts.sort(key=lambda p: (p["date"], p["platform"]))

    return {
        "meta": {
            "start_date":     start.isoformat(),
            "end_date":       (start + timedelta(weeks=weeks) - timedelta(days=1)).isoformat(),
            "weeks":          weeks,
            "platforms":      [p["name"] for p in platforms],
            "total_posts":    len(all_posts),
            "pillars":        [p["name"] for p in pillars],
        },
        "platforms": calendar_by_platform,
        "timeline":  all_posts,   # merged, date-sorted
    }

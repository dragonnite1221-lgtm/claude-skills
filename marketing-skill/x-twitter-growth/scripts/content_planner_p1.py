# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_planner_base import *  # noqa: F403,E402


CONTENT_FORMATS = {
    "atomic_tweet": {"growth_weight": 0.3, "effort": "low", "description": "Single tweet — observation, tip, or hot take"},
    "thread": {"growth_weight": 0.35, "effort": "high", "description": "5-12 tweet deep dive — highest reach potential"},
    "question": {"growth_weight": 0.15, "effort": "low", "description": "Engagement bait — drives replies"},
    "quote_tweet": {"growth_weight": 0.10, "effort": "low", "description": "Add value to someone else's content"},
    "reply_session": {"growth_weight": 0.10, "effort": "medium", "description": "30 min focused engagement on target accounts"},
}
OPTIMAL_TIMES = {
    "weekday": ["07:00-08:00", "12:00-13:00", "17:00-18:00", "20:00-21:00"],
    "weekend": ["09:00-10:00", "14:00-15:00", "19:00-20:00"],
}
TOPIC_ANGLES = [
    "Lessons learned (personal experience)",
    "Framework/system breakdown",
    "Tool recommendation (with honest take)",
    "Myth busting (challenge common belief)",
    "Behind the scenes (process, workflow)",
    "Industry trend analysis",
    "Beginner guide (explain like I'm 5)",
    "Comparison (X vs Y — which is better?)",
    "Prediction (what's coming next)",
    "Case study (real example with numbers)",
    "Mistake I made (vulnerability + lesson)",
    "Quick tip (tactical, immediately useful)",
    "Controversial take (spicy but defensible)",
    "Curated list (best resources, tools, accounts)",
]
@dataclass
class DayPlan:
    date: str
    day_of_week: str
    posts: list = field(default_factory=list)
    engagement_target: str = ""
@dataclass
class PostSlot:
    time: str
    format: str
    topic_angle: str
    topic_suggestion: str
    notes: str = ""
@dataclass
class WeekPlan:
    week_number: int
    start_date: str
    end_date: str
    days: list = field(default_factory=list)
    thread_count: int = 0
    total_posts: int = 0
    focus_theme: str = ""
def generate_plan(niche: str, posts_per_day: int, weeks: int, start_date: datetime) -> list:
    plans = []
    angle_idx = 0
    time_idx = 0

    for week in range(weeks):
        week_start = start_date + timedelta(weeks=week)
        week_end = week_start + timedelta(days=6)

        week_plan = WeekPlan(
            week_number=week + 1,
            start_date=week_start.strftime("%Y-%m-%d"),
            end_date=week_end.strftime("%Y-%m-%d"),
            focus_theme=TOPIC_ANGLES[week % len(TOPIC_ANGLES)],
        )

        for day in range(7):
            current = week_start + timedelta(days=day)
            day_name = current.strftime("%A")
            is_weekend = day >= 5

            times = OPTIMAL_TIMES["weekend" if is_weekend else "weekday"]
            actual_posts = max(1, posts_per_day - (1 if is_weekend else 0))

            day_plan = DayPlan(
                date=current.strftime("%Y-%m-%d"),
                day_of_week=day_name,
                engagement_target="15 min reply session" if is_weekend else "30 min reply session",
            )

            for p in range(actual_posts):
                # Determine format based on day position
                if day in [1, 3] and p == 0:  # Tue/Thu first slot = thread
                    fmt = "thread"
                elif p == actual_posts - 1 and not is_weekend:
                    fmt = "question"  # Last post = engagement driver
                elif day == 4 and p == 0:  # Friday first = quote tweet
                    fmt = "quote_tweet"
                else:
                    fmt = "atomic_tweet"

                angle = TOPIC_ANGLES[angle_idx % len(TOPIC_ANGLES)]
                angle_idx += 1

                slot = PostSlot(
                    time=times[p % len(times)],
                    format=fmt,
                    topic_angle=angle,
                    topic_suggestion=f"{angle} about {niche}",
                    notes="Pin if performs well" if fmt == "thread" else "",
                )
                day_plan.posts.append(asdict(slot))

                if fmt == "thread":
                    week_plan.thread_count += 1
                week_plan.total_posts += 1

            week_plan.days.append(asdict(day_plan))

        plans.append(asdict(week_plan))

    return plans

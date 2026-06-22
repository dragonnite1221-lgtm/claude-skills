# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from social_calendar_generator_base import *  # noqa: F403,E402


DEMO_CONFIG = {
    "pillars": [
        {"name": "Educational",   "description": "Tips, tutorials, how-tos", "emoji": "🎓", "weight": 3},
        {"name": "Inspirational", "description": "Success stories & quotes",  "emoji": "✨", "weight": 2},
        {"name": "Product",       "description": "Feature demos & updates",   "emoji": "🛠 ", "weight": 2},
        {"name": "Community",     "description": "UGC, polls & shoutouts",    "emoji": "🤝", "weight": 1},
    ],
    "platforms": [
        {
            "name": "LinkedIn",
            "posts_per_week": 3,
            "best_days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
            "content_type_hint": "Long-form insights, carousels, thought leadership",
        },
        {
            "name": "Twitter/X",
            "posts_per_week": 5,
            "best_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "content_type_hint": "Threads, quick tips, hot takes, polls",
        },
    ],
    "start_date": None,   # defaults to next Monday
    "weeks": 4,
}
CONTENT_TYPE_HINTS = {
    "Educational":   ["How-to thread", "Quick tip", "Carousel: 5 steps", "Tutorial link"],
    "Inspirational": ["Quote image", "Success story", "Before/after", "Motivational thread"],
    "Product":       ["Feature demo GIF", "Changelog post", "Use-case spotlight", "Behind the scenes"],
    "Community":     ["Poll", "User shoutout", "Question post", "Community highlight"],
}
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def build_pillar_sequence(pillars: list, length: int) -> list:
    """
    Build a balanced pillar rotation of `length` posts using weighted distribution.
    Uses a deterministic greedy algorithm (no random, reproducible).
    """
    names   = [p["name"] for p in pillars]
    weights = [p.get("weight", 1) for p in pillars]
    total_w = sum(weights)

    # Target proportion per pillar
    targets = [w / total_w for w in weights]

    sequence = []
    counts   = [0] * len(pillars)

    for _ in range(length):
        # Pick pillar most "behind" its target proportion
        scores = []
        for i, name in enumerate(names):
            current_prop = counts[i] / (len(sequence) + 1) if sequence else 0
            scores.append(targets[i] - current_prop)
        best = scores.index(max(scores))
        sequence.append(names[best])
        counts[best] += 1

    return sequence
def next_monday(from_date: date = None) -> date:
    d = from_date or date.today()
    days_ahead = (0 - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return d + timedelta(days=days_ahead)
def parse_date(s: str) -> date:
    return date.fromisoformat(s)

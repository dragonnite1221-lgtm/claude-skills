# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from attribution_analyzer_base import *  # noqa: F403,E402


MODELS = ["first-touch", "last-touch", "linear", "time-decay", "position-based"]
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def parse_timestamp(ts: str) -> datetime:
    """Parse an ISO-format timestamp string into a datetime object."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {ts}")
def first_touch_attribution(journeys: List[Dict]) -> Dict[str, float]:
    """First-touch: 100% credit to the first touchpoint in each journey."""
    credits: Dict[str, float] = {}
    for journey in journeys:
        if not journey.get("converted", False):
            continue
        touchpoints = journey.get("touchpoints", [])
        if not touchpoints:
            continue
        sorted_tp = sorted(touchpoints, key=lambda t: parse_timestamp(t["timestamp"]))
        channel = sorted_tp[0]["channel"]
        revenue = journey.get("revenue", 1.0)
        credits[channel] = credits.get(channel, 0.0) + revenue
    return credits
def last_touch_attribution(journeys: List[Dict]) -> Dict[str, float]:
    """Last-touch: 100% credit to the last touchpoint in each journey."""
    credits: Dict[str, float] = {}
    for journey in journeys:
        if not journey.get("converted", False):
            continue
        touchpoints = journey.get("touchpoints", [])
        if not touchpoints:
            continue
        sorted_tp = sorted(touchpoints, key=lambda t: parse_timestamp(t["timestamp"]))
        channel = sorted_tp[-1]["channel"]
        revenue = journey.get("revenue", 1.0)
        credits[channel] = credits.get(channel, 0.0) + revenue
    return credits
def linear_attribution(journeys: List[Dict]) -> Dict[str, float]:
    """Linear: Equal credit split across all touchpoints in each journey."""
    credits: Dict[str, float] = {}
    for journey in journeys:
        if not journey.get("converted", False):
            continue
        touchpoints = journey.get("touchpoints", [])
        if not touchpoints:
            continue
        revenue = journey.get("revenue", 1.0)
        share = safe_divide(revenue, len(touchpoints))
        for tp in touchpoints:
            channel = tp["channel"]
            credits[channel] = credits.get(channel, 0.0) + share
    return credits
def time_decay_attribution(journeys: List[Dict], half_life_days: float = 7.0) -> Dict[str, float]:
    """Time-decay: Exponential decay giving more credit to recent touchpoints.

    Uses a configurable half-life (in days). Touchpoints closer to conversion
    receive exponentially more credit.
    """
    import math

    credits: Dict[str, float] = {}
    decay_rate = math.log(2) / half_life_days

    for journey in journeys:
        if not journey.get("converted", False):
            continue
        touchpoints = journey.get("touchpoints", [])
        if not touchpoints:
            continue

        revenue = journey.get("revenue", 1.0)
        sorted_tp = sorted(touchpoints, key=lambda t: parse_timestamp(t["timestamp"]))
        conversion_time = parse_timestamp(sorted_tp[-1]["timestamp"])

        # Calculate raw weights
        weights: List[float] = []
        for tp in sorted_tp:
            tp_time = parse_timestamp(tp["timestamp"])
            days_before = (conversion_time - tp_time).total_seconds() / 86400.0
            weight = math.exp(-decay_rate * days_before)
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight == 0:
            continue

        for i, tp in enumerate(sorted_tp):
            channel = tp["channel"]
            share = safe_divide(weights[i], total_weight) * revenue
            credits[channel] = credits.get(channel, 0.0) + share

    return credits

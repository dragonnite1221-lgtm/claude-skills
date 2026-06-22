# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from attribution_analyzer_base import *  # noqa: F403,E402
# fmt: off
from attribution_analyzer_p1 import MODELS, first_touch_attribution, last_touch_attribution, linear_attribution, parse_timestamp, safe_divide, time_decay_attribution  # noqa: E402,E501
# fmt: on


def position_based_attribution(journeys: List[Dict]) -> Dict[str, float]:
    """Position-based: 40% first, 40% last, 20% split among middle touchpoints."""
    credits: Dict[str, float] = {}
    for journey in journeys:
        if not journey.get("converted", False):
            continue
        touchpoints = journey.get("touchpoints", [])
        if not touchpoints:
            continue

        revenue = journey.get("revenue", 1.0)
        sorted_tp = sorted(touchpoints, key=lambda t: parse_timestamp(t["timestamp"]))

        if len(sorted_tp) == 1:
            channel = sorted_tp[0]["channel"]
            credits[channel] = credits.get(channel, 0.0) + revenue
        elif len(sorted_tp) == 2:
            first_channel = sorted_tp[0]["channel"]
            last_channel = sorted_tp[-1]["channel"]
            credits[first_channel] = credits.get(first_channel, 0.0) + revenue * 0.5
            credits[last_channel] = credits.get(last_channel, 0.0) + revenue * 0.5
        else:
            first_channel = sorted_tp[0]["channel"]
            last_channel = sorted_tp[-1]["channel"]
            credits[first_channel] = credits.get(first_channel, 0.0) + revenue * 0.4
            credits[last_channel] = credits.get(last_channel, 0.0) + revenue * 0.4

            middle_count = len(sorted_tp) - 2
            middle_share = safe_divide(revenue * 0.2, middle_count)
            for tp in sorted_tp[1:-1]:
                channel = tp["channel"]
                credits[channel] = credits.get(channel, 0.0) + middle_share

    return credits
def run_model(model_name: str, journeys: List[Dict], half_life: float = 7.0) -> Dict[str, float]:
    """Dispatch to the appropriate attribution model."""
    if model_name == "first-touch":
        return first_touch_attribution(journeys)
    elif model_name == "last-touch":
        return last_touch_attribution(journeys)
    elif model_name == "linear":
        return linear_attribution(journeys)
    elif model_name == "time-decay":
        return time_decay_attribution(journeys, half_life)
    elif model_name == "position-based":
        return position_based_attribution(journeys)
    else:
        raise ValueError(f"Unknown model: {model_name}. Choose from: {', '.join(MODELS)}")
def compute_summary(journeys: List[Dict]) -> Dict[str, Any]:
    """Compute summary statistics about the journey data."""
    total_journeys = len(journeys)
    converted = sum(1 for j in journeys if j.get("converted", False))
    total_revenue = sum(j.get("revenue", 0.0) for j in journeys if j.get("converted", False))
    all_channels = set()
    for j in journeys:
        for tp in j.get("touchpoints", []):
            all_channels.add(tp["channel"])

    return {
        "total_journeys": total_journeys,
        "converted_journeys": converted,
        "conversion_rate": round(safe_divide(converted, total_journeys) * 100, 2),
        "total_revenue": round(total_revenue, 2),
        "channels_observed": sorted(all_channels),
    }

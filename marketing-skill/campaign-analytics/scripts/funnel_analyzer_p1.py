# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_analyzer_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def analyze_funnel(stages: List[str], counts: List[int]) -> Dict[str, Any]:
    """Analyze a single funnel and return stage-by-stage metrics.

    Args:
        stages: Ordered list of funnel stage names (top to bottom).
        counts: Corresponding counts at each stage.

    Returns:
        Dictionary with stage metrics, bottleneck info, and overall conversion.
    """
    if len(stages) != len(counts):
        raise ValueError("Number of stages must match number of counts.")
    if not stages:
        raise ValueError("Funnel must have at least one stage.")

    stage_metrics: List[Dict[str, Any]] = []
    max_dropoff_abs = 0
    max_dropoff_rel = 0.0
    bottleneck_abs: Optional[str] = None
    bottleneck_rel: Optional[str] = None

    for i, (stage, count) in enumerate(zip(stages, counts)):
        metric: Dict[str, Any] = {
            "stage": stage,
            "count": count,
            "cumulative_conversion": round(safe_divide(count, counts[0]) * 100, 2),
        }

        if i > 0:
            prev_count = counts[i - 1]
            dropoff = prev_count - count
            conversion_rate = safe_divide(count, prev_count) * 100
            dropoff_rate = 100 - conversion_rate

            metric["from_previous"] = stages[i - 1]
            metric["conversion_rate"] = round(conversion_rate, 2)
            metric["dropoff_count"] = dropoff
            metric["dropoff_rate"] = round(dropoff_rate, 2)

            # Track biggest absolute drop-off
            if dropoff > max_dropoff_abs:
                max_dropoff_abs = dropoff
                bottleneck_abs = f"{stages[i-1]} -> {stage}"

            # Track biggest relative drop-off
            if dropoff_rate > max_dropoff_rel:
                max_dropoff_rel = dropoff_rate
                bottleneck_rel = f"{stages[i-1]} -> {stage}"
        else:
            metric["conversion_rate"] = 100.0
            metric["dropoff_count"] = 0
            metric["dropoff_rate"] = 0.0

        stage_metrics.append(metric)

    overall_conversion = safe_divide(counts[-1], counts[0]) * 100

    return {
        "stage_metrics": stage_metrics,
        "overall_conversion_rate": round(overall_conversion, 2),
        "total_entries": counts[0],
        "total_conversions": counts[-1],
        "total_lost": counts[0] - counts[-1],
        "bottleneck_absolute": {
            "transition": bottleneck_abs,
            "dropoff_count": max_dropoff_abs,
        },
        "bottleneck_relative": {
            "transition": bottleneck_rel,
            "dropoff_rate": round(max_dropoff_rel, 2),
        },
    }

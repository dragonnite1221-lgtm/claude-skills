# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from campaign_roi_calculator_base import *  # noqa: F403,E402


BENCHMARKS: Dict[str, Dict[str, tuple]] = {
    "ctr": {
        "email": (1.0, 2.5, 5.0),
        "paid_search": (1.5, 3.5, 7.0),
        "paid_social": (0.5, 1.2, 3.0),
        "display": (0.05, 0.1, 0.5),
        "organic_search": (1.5, 3.0, 8.0),
        "organic_social": (0.5, 1.5, 4.0),
        "referral": (1.0, 3.0, 6.0),
        "direct": (2.0, 4.0, 8.0),
        "default": (0.5, 2.0, 5.0),
    },
    "roas": {
        "email": (30.0, 42.0, 60.0),
        "paid_search": (2.0, 4.0, 8.0),
        "paid_social": (1.5, 3.0, 6.0),
        "display": (0.5, 1.5, 3.0),
        "organic_search": (5.0, 10.0, 20.0),
        "organic_social": (3.0, 6.0, 12.0),
        "referral": (3.0, 5.0, 10.0),
        "direct": (4.0, 8.0, 15.0),
        "default": (2.0, 4.0, 8.0),
    },
    "cpa": {
        "email": (5.0, 15.0, 40.0),
        "paid_search": (20.0, 50.0, 150.0),
        "paid_social": (15.0, 40.0, 100.0),
        "display": (30.0, 75.0, 200.0),
        "organic_search": (5.0, 20.0, 60.0),
        "organic_social": (10.0, 30.0, 80.0),
        "referral": (10.0, 25.0, 70.0),
        "direct": (5.0, 15.0, 50.0),
        "default": (15.0, 45.0, 120.0),
    },
}
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def get_benchmark(metric: str, channel: str) -> tuple:
    """Get benchmark range for a metric and channel.

    Returns:
        Tuple of (low, target, high) for the given metric and channel.
    """
    metric_benchmarks = BENCHMARKS.get(metric, {})
    return metric_benchmarks.get(channel, metric_benchmarks.get("default", (0, 0, 0)))
def assess_performance(value: float, benchmark: tuple, higher_is_better: bool = True) -> str:
    """Assess a metric value against its benchmark range.

    Args:
        value: The metric value to assess.
        benchmark: Tuple of (low, target, high).
        higher_is_better: Whether higher values are better (True for CTR, ROAS; False for CPA).

    Returns:
        Performance assessment string.
    """
    low, target, high = benchmark

    if higher_is_better:
        if value >= high:
            return "excellent"
        elif value >= target:
            return "good"
        elif value >= low:
            return "below_target"
        else:
            return "underperforming"
    else:
        # For cost metrics, lower is better
        if value <= low:
            return "excellent"
        elif value <= target:
            return "good"
        elif value <= high:
            return "below_target"
        else:
            return "underperforming"

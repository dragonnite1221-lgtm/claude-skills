# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_accuracy_tracker_base import *  # noqa: F403,E402
# fmt: off
from forecast_accuracy_tracker_p1 import calculate_mape, safe_divide  # noqa: E402,E501
# fmt: on


def analyze_bias(periods: list[dict]) -> dict[str, Any]:
    """Analyze systematic forecasting bias.

    Positive bias = over-forecasting (forecast > actual, i.e., actual fell short)
    Negative bias = under-forecasting (forecast < actual, i.e., actual exceeded)

    Args:
        periods: List of dicts with 'forecast' and 'actual' keys.

    Returns:
        Bias analysis with direction, magnitude, and ratio.
    """
    if not periods:
        return {
            "direction": "None",
            "bias_pct": 0.0,
            "over_forecast_count": 0,
            "under_forecast_count": 0,
            "exact_count": 0,
            "bias_ratio": 0.0,
        }

    over_count = 0
    under_count = 0
    exact_count = 0
    total_bias = 0.0

    for p in periods:
        diff = p["forecast"] - p["actual"]
        total_bias += diff
        if diff > 0:
            over_count += 1
        elif diff < 0:
            under_count += 1
        else:
            exact_count += 1

    avg_bias = total_bias / len(periods)
    total_actual = sum(p["actual"] for p in periods)
    bias_pct = safe_divide(total_bias, total_actual) * 100

    if over_count > under_count:
        direction = "Over-forecasting"
    elif under_count > over_count:
        direction = "Under-forecasting"
    else:
        direction = "Balanced"

    bias_ratio = safe_divide(over_count, over_count + under_count)

    return {
        "direction": direction,
        "avg_bias_amount": round(avg_bias, 2),
        "bias_pct": round(bias_pct, 1),
        "over_forecast_count": over_count,
        "under_forecast_count": under_count,
        "exact_count": exact_count,
        "bias_ratio": round(bias_ratio, 2),
    }
def analyze_trend(periods: list[dict]) -> dict[str, Any]:
    """Analyze period-over-period accuracy trend.

    Determines if forecast accuracy is improving, stable, or declining
    by comparing error rates across consecutive periods.

    Args:
        periods: List of dicts with 'period', 'forecast', and 'actual' keys.

    Returns:
        Trend analysis with direction and period details.
    """
    if len(periods) < 2:
        return {
            "trend": "Insufficient data",
            "period_errors": [],
            "improving_periods": 0,
            "declining_periods": 0,
        }

    period_errors = []
    for p in periods:
        actual = p["actual"]
        forecast = p["forecast"]
        if actual != 0:
            error_pct = abs(actual - forecast) / abs(actual) * 100
        else:
            error_pct = 0.0
        period_errors.append({
            "period": p.get("period", "Unknown"),
            "error_pct": round(error_pct, 1),
            "forecast": forecast,
            "actual": actual,
        })

    improving = 0
    declining = 0
    for i in range(1, len(period_errors)):
        if period_errors[i]["error_pct"] < period_errors[i - 1]["error_pct"]:
            improving += 1
        elif period_errors[i]["error_pct"] > period_errors[i - 1]["error_pct"]:
            declining += 1

    if improving > declining:
        trend = "Improving"
    elif declining > improving:
        trend = "Declining"
    else:
        trend = "Stable"

    # Calculate recent vs historical MAPE
    midpoint = len(periods) // 2
    if midpoint > 0:
        early_mape = calculate_mape(periods[:midpoint])
        recent_mape = calculate_mape(periods[midpoint:])
        mape_change = recent_mape - early_mape
    else:
        early_mape = 0.0
        recent_mape = 0.0
        mape_change = 0.0

    return {
        "trend": trend,
        "period_errors": period_errors,
        "improving_periods": improving,
        "declining_periods": declining,
        "early_mape": round(early_mape, 1),
        "recent_mape": round(recent_mape, 1),
        "mape_change": round(mape_change, 1),
    }

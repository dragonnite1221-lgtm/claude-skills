# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_accuracy_tracker_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def calculate_mape(periods: list[dict]) -> float:
    """Calculate Mean Absolute Percentage Error.

    Formula: mean(|actual - forecast| / |actual|) x 100

    Args:
        periods: List of dicts with 'forecast' and 'actual' keys.

    Returns:
        MAPE as a percentage.
    """
    if not periods:
        return 0.0

    errors = []
    for p in periods:
        actual = p["actual"]
        forecast = p["forecast"]
        if actual != 0:
            errors.append(abs(actual - forecast) / abs(actual))

    if not errors:
        return 0.0

    return (sum(errors) / len(errors)) * 100
def calculate_weighted_mape(periods: list[dict]) -> float:
    """Calculate value-weighted MAPE.

    Weights each period's error by its actual value, giving more importance
    to larger periods.

    Args:
        periods: List of dicts with 'forecast' and 'actual' keys.

    Returns:
        Weighted MAPE as a percentage.
    """
    if not periods:
        return 0.0

    total_actual = sum(abs(p["actual"]) for p in periods)
    if total_actual == 0:
        return 0.0

    weighted_errors = 0.0
    for p in periods:
        actual = p["actual"]
        forecast = p["forecast"]
        if actual != 0:
            weight = abs(actual) / total_actual
            weighted_errors += weight * (abs(actual - forecast) / abs(actual))

    return weighted_errors * 100
def get_accuracy_rating(mape: float) -> dict[str, str]:
    """Return accuracy rating based on MAPE threshold.

    Ratings:
        Excellent: <10%
        Good: 10-15%
        Fair: 15-25%
        Poor: >25%
    """
    if mape < 10:
        return {"rating": "Excellent", "description": "Highly predictable, data-driven process"}
    elif mape < 15:
        return {"rating": "Good", "description": "Reliable forecasting with minor variance"}
    elif mape < 25:
        return {"rating": "Fair", "description": "Needs process improvement"}
    else:
        return {"rating": "Poor", "description": "Significant forecasting methodology gaps"}

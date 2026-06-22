# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
BENCHMARKS = {
    "magic_number": {
        "green": {"min": 0.75, "label": ">0.75 - Efficient GTM spend"},
        "yellow": {"min": 0.50, "max": 0.75, "label": "0.50-0.75 - Acceptable efficiency"},
        "red": {"max": 0.50, "label": "<0.50 - Inefficient GTM spend"},
        "elite": 1.0,
        "description": "Net New ARR / Prior Period S&M Spend",
    },
    "ltv_cac_ratio": {
        "green": {"min": 3.0, "label": ">3:1 - Strong unit economics"},
        "yellow": {"min": 1.0, "max": 3.0, "label": "1:1-3:1 - Marginal unit economics"},
        "red": {"max": 1.0, "label": "<1:1 - Unsustainable unit economics"},
        "elite": 5.0,
        "description": "Customer LTV / Customer Acquisition Cost",
    },
    "cac_payback_months": {
        "green": {"max": 18, "label": "<18 months - Healthy payback"},
        "yellow": {"min": 18, "max": 24, "label": "18-24 months - Acceptable payback"},
        "red": {"min": 24, "label": ">24 months - Capital intensive"},
        "elite": 12,
        "description": "CAC / (ARPA x Gross Margin) in months",
    },
    "burn_multiple": {
        "green": {"max": 2.0, "label": "<2x - Capital efficient growth"},
        "yellow": {"min": 2.0, "max": 4.0, "label": "2-4x - Moderate burn"},
        "red": {"min": 4.0, "label": ">4x - Unsustainable burn"},
        "elite": 1.0,
        "description": "Net Burn / Net New ARR",
    },
    "rule_of_40": {
        "green": {"min": 40, "label": ">40% - Strong balance of growth & profitability"},
        "yellow": {"min": 20, "max": 40, "label": "20-40% - Acceptable balance"},
        "red": {"max": 20, "label": "<20% - Needs improvement"},
        "elite": 60,
        "description": "Revenue Growth % + FCF Margin %",
    },
    "ndr_pct": {
        "green": {"min": 110, "label": ">110% - Strong expansion revenue"},
        "yellow": {"min": 100, "max": 110, "label": "100-110% - Stable base"},
        "red": {"max": 100, "label": "<100% - Net revenue contraction"},
        "elite": 130,
        "description": "(Begin ARR + Expansion - Contraction - Churn) / Begin ARR",
    },
}
def rate_metric(metric_name: str, value: float) -> dict[str, str]:
    """Rate a metric as Green/Yellow/Red based on benchmark thresholds.

    Args:
        metric_name: Key into BENCHMARKS dict.
        value: The metric value to rate.

    Returns:
        Dict with rating color, label, and percentile guidance.
    """
    bench = BENCHMARKS.get(metric_name)
    if not bench:
        return {"rating": "Unknown", "label": "No benchmark available"}

    # For metrics where lower is better (cac_payback, burn_multiple)
    lower_is_better = metric_name in ("cac_payback_months", "burn_multiple")

    if lower_is_better:
        if "max" in bench["green"] and value <= bench["green"]["max"]:
            rating = "Green"
            label = bench["green"]["label"]
        elif "min" in bench.get("yellow", {}) and "max" in bench.get("yellow", {}):
            if bench["yellow"]["min"] <= value <= bench["yellow"]["max"]:
                rating = "Yellow"
                label = bench["yellow"]["label"]
            else:
                rating = "Red"
                label = bench["red"]["label"]
        else:
            rating = "Red"
            label = bench["red"]["label"]
    else:
        if "min" in bench["green"] and value >= bench["green"]["min"]:
            rating = "Green"
            label = bench["green"]["label"]
        elif "min" in bench.get("yellow", {}) and "max" in bench.get("yellow", {}):
            if bench["yellow"]["min"] <= value <= bench["yellow"]["max"]:
                rating = "Yellow"
                label = bench["yellow"]["label"]
            else:
                rating = "Red"
                label = bench["red"]["label"]
        else:
            rating = "Red"
            label = bench["red"]["label"]

    # Percentile placement (simplified)
    elite = bench.get("elite", 0)
    if lower_is_better:
        if elite > 0 and value > 0:
            if value <= elite:
                percentile = "Top 10%"
            elif rating == "Green":
                percentile = "Top 25%"
            elif rating == "Yellow":
                percentile = "Median"
            else:
                percentile = "Below median"
        else:
            percentile = "N/A"
    else:
        if elite > 0:
            if value >= elite:
                percentile = "Top 10%"
            elif rating == "Green":
                percentile = "Top 25%"
            elif rating == "Yellow":
                percentile = "Median"
            else:
                percentile = "Below median"
        else:
            percentile = "N/A"

    return {
        "rating": rating,
        "label": label,
        "percentile": percentile,
    }

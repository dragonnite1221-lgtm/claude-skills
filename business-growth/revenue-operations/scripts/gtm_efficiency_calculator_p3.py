# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402
# fmt: off
from gtm_efficiency_calculator_p1 import rate_metric, safe_divide  # noqa: E402,E501
# fmt: on


def calculate_rule_of_40(
    revenue_growth_pct: float, fcf_margin_pct: float
) -> dict[str, Any]:
    """Calculate Rule of 40.

    Formula: Revenue Growth % + FCF Margin %
    Target: >40%

    Args:
        revenue_growth_pct: Year-over-year revenue growth percentage.
        fcf_margin_pct: Free cash flow margin percentage.

    Returns:
        Rule of 40 score with rating and benchmark.
    """
    value = revenue_growth_pct + fcf_margin_pct
    benchmark = rate_metric("rule_of_40", value)

    return {
        "value": round(value, 1),
        "revenue_growth_pct": revenue_growth_pct,
        "fcf_margin_pct": fcf_margin_pct,
        "formula": "Revenue Growth % + FCF Margin %",
        "target": ">40%",
        **benchmark,
    }
def calculate_ndr(
    beginning_arr: float,
    expansion_arr: float,
    contraction_arr: float,
    churned_arr: float,
) -> dict[str, Any]:
    """Calculate Net Dollar Retention.

    Formula: (Beginning ARR + Expansion - Contraction - Churn) / Beginning ARR
    Target: >110%

    Args:
        beginning_arr: ARR at start of period.
        expansion_arr: Expansion revenue from existing customers.
        contraction_arr: Revenue lost from downgrades.
        churned_arr: Revenue lost from customer churn.

    Returns:
        NDR percentage with rating and benchmark.
    """
    ending_arr = beginning_arr + expansion_arr - contraction_arr - churned_arr
    ndr_pct = safe_divide(ending_arr, beginning_arr) * 100

    benchmark = rate_metric("ndr_pct", ndr_pct)

    return {
        "ndr_pct": round(ndr_pct, 1),
        "beginning_arr": beginning_arr,
        "expansion_arr": expansion_arr,
        "contraction_arr": contraction_arr,
        "churned_arr": churned_arr,
        "ending_arr": round(ending_arr, 2),
        "formula": "(Begin ARR + Expansion - Contraction - Churn) / Begin ARR",
        "target": ">110%",
        **benchmark,
    }

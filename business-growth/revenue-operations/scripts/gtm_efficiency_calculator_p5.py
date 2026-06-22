# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402
# fmt: off
from gtm_efficiency_calculator_p2 import calculate_burn_multiple, calculate_cac_payback, calculate_ltv_cac, calculate_magic_number  # noqa: E402,E501
from gtm_efficiency_calculator_p3 import calculate_ndr, calculate_rule_of_40  # noqa: E402,E501
from gtm_efficiency_calculator_p4 import generate_recommendations  # noqa: E402,E501
# fmt: on


def calculate_all_metrics(data: dict) -> dict[str, Any]:
    """Calculate all GTM efficiency metrics from input data.

    Args:
        data: Input data with revenue, costs, and customers sections.

    Returns:
        Complete GTM efficiency analysis results.
    """
    revenue = data["revenue"]
    costs = data["costs"]
    customers = data["customers"]

    metrics = {
        "magic_number": calculate_magic_number(
            net_new_arr=revenue["net_new_arr"],
            sm_spend=costs["sales_marketing_spend"],
        ),
        "ltv_cac": calculate_ltv_cac(
            arpa_monthly=revenue["arpa_monthly"],
            gross_margin_pct=costs["gross_margin_pct"],
            annual_churn_rate_pct=customers["annual_churn_rate_pct"],
            cac=costs["cac"],
        ),
        "cac_payback": calculate_cac_payback(
            cac=costs["cac"],
            arpa_monthly=revenue["arpa_monthly"],
            gross_margin_pct=costs["gross_margin_pct"],
        ),
        "burn_multiple": calculate_burn_multiple(
            net_burn=costs["net_burn"],
            net_new_arr=revenue["net_new_arr"],
        ),
        "rule_of_40": calculate_rule_of_40(
            revenue_growth_pct=revenue["revenue_growth_pct"],
            fcf_margin_pct=costs["fcf_margin_pct"],
        ),
        "ndr": calculate_ndr(
            beginning_arr=customers["beginning_arr"],
            expansion_arr=customers["expansion_arr"],
            contraction_arr=customers["contraction_arr"],
            churned_arr=customers["churned_arr"],
        ),
    }

    metrics["recommendations"] = generate_recommendations(metrics)

    return metrics
def format_currency(value: float) -> str:
    """Format a number as currency."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"

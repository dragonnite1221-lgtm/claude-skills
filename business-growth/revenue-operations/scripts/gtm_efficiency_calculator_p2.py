# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402
# fmt: off
from gtm_efficiency_calculator_p1 import rate_metric, safe_divide  # noqa: E402,E501
# fmt: on


def calculate_magic_number(net_new_arr: float, sm_spend: float) -> dict[str, Any]:
    """Calculate Magic Number.

    Formula: Net New ARR / Prior Period S&M Spend
    Target: >0.75

    Args:
        net_new_arr: Net new annual recurring revenue in the period.
        sm_spend: Sales & marketing spend in the prior period.

    Returns:
        Magic number value with rating and benchmark.
    """
    value = safe_divide(net_new_arr, sm_spend)
    benchmark = rate_metric("magic_number", value)

    return {
        "value": round(value, 2),
        "net_new_arr": net_new_arr,
        "sm_spend": sm_spend,
        "formula": "Net New ARR / Prior Period S&M Spend",
        "target": ">0.75",
        **benchmark,
    }
def calculate_ltv_cac(
    arpa_monthly: float,
    gross_margin_pct: float,
    annual_churn_rate_pct: float,
    cac: float,
) -> dict[str, Any]:
    """Calculate LTV:CAC Ratio.

    LTV = ARPA_monthly x 12 x Gross Margin / Annual Churn Rate
    Ratio = LTV / CAC
    Target: >3:1

    Args:
        arpa_monthly: Average revenue per account per month.
        gross_margin_pct: Gross margin as percentage (e.g., 78 for 78%).
        annual_churn_rate_pct: Annual churn rate as percentage (e.g., 8 for 8%).
        cac: Customer acquisition cost.

    Returns:
        LTV:CAC ratio with component values, rating, and benchmark.
    """
    gross_margin = gross_margin_pct / 100
    churn_rate = annual_churn_rate_pct / 100

    arpa_annual = arpa_monthly * 12
    ltv = safe_divide(arpa_annual * gross_margin, churn_rate)
    ratio = safe_divide(ltv, cac)

    benchmark = rate_metric("ltv_cac_ratio", ratio)

    return {
        "ratio": round(ratio, 1),
        "ltv": round(ltv, 2),
        "cac": cac,
        "arpa_monthly": arpa_monthly,
        "arpa_annual": arpa_annual,
        "gross_margin_pct": gross_margin_pct,
        "annual_churn_rate_pct": annual_churn_rate_pct,
        "formula": "LTV (ARPA x Gross Margin / Churn Rate) / CAC",
        "target": ">3:1",
        **benchmark,
    }
def calculate_cac_payback(
    cac: float, arpa_monthly: float, gross_margin_pct: float
) -> dict[str, Any]:
    """Calculate CAC Payback Period.

    Formula: CAC / (ARPA_monthly x Gross Margin) in months
    Target: <18 months

    Args:
        cac: Customer acquisition cost.
        arpa_monthly: Average revenue per account per month.
        gross_margin_pct: Gross margin as percentage.

    Returns:
        CAC payback months with rating and benchmark.
    """
    gross_margin = gross_margin_pct / 100
    monthly_contribution = arpa_monthly * gross_margin
    payback_months = safe_divide(cac, monthly_contribution)

    benchmark = rate_metric("cac_payback_months", payback_months)

    return {
        "months": round(payback_months, 1),
        "cac": cac,
        "arpa_monthly": arpa_monthly,
        "gross_margin_pct": gross_margin_pct,
        "monthly_contribution": round(monthly_contribution, 2),
        "formula": "CAC / (ARPA_monthly x Gross Margin)",
        "target": "<18 months",
        **benchmark,
    }
def calculate_burn_multiple(net_burn: float, net_new_arr: float) -> dict[str, Any]:
    """Calculate Burn Multiple.

    Formula: Net Burn / Net New ARR
    Target: <2x (lower is better)

    Args:
        net_burn: Net cash burn in the period.
        net_new_arr: Net new ARR added in the period.

    Returns:
        Burn multiple with rating and benchmark.
    """
    value = safe_divide(net_burn, net_new_arr)
    benchmark = rate_metric("burn_multiple", value)

    return {
        "value": round(value, 2),
        "net_burn": net_burn,
        "net_new_arr": net_new_arr,
        "formula": "Net Burn / Net New ARR",
        "target": "<2x",
        **benchmark,
    }

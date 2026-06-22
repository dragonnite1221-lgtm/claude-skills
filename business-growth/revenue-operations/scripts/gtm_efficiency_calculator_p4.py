# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402


def generate_recommendations(metrics: dict) -> list[str]:
    """Generate strategic recommendations based on GTM efficiency metrics.

    Args:
        metrics: Dict of all calculated metric results.

    Returns:
        List of recommendation strings.
    """
    recs = []

    # Magic Number
    mn = metrics["magic_number"]
    if mn["rating"] == "Red":
        recs.append(
            f"Magic Number is {mn['value']} (target >0.75). GTM spend is inefficient. "
            "Audit channel ROI, optimize sales productivity, and consider reducing "
            "low-performing spend."
        )
    elif mn["rating"] == "Yellow":
        recs.append(
            f"Magic Number is {mn['value']}. GTM efficiency is acceptable but can improve. "
            "Focus on sales enablement and pipeline quality over quantity."
        )

    # LTV:CAC
    lc = metrics["ltv_cac"]
    if lc["rating"] == "Red":
        recs.append(
            f"LTV:CAC ratio is {lc['ratio']}:1 (target >3:1). Unit economics are unsustainable. "
            "Reduce CAC through better targeting, improve retention to increase LTV, "
            "or increase ARPA through pricing optimization."
        )
    elif lc["rating"] == "Yellow":
        recs.append(
            f"LTV:CAC ratio is {lc['ratio']}:1. Unit economics are marginal. "
            "Focus on reducing churn and expanding within existing accounts."
        )

    # CAC Payback
    cp = metrics["cac_payback"]
    if cp["rating"] == "Red":
        recs.append(
            f"CAC payback is {cp['months']} months (target <18). Capital recovery is too slow. "
            "Reduce acquisition costs or increase gross-margin-weighted ARPA."
        )

    # Burn Multiple
    bm = metrics["burn_multiple"]
    if bm["rating"] == "Red":
        recs.append(
            f"Burn multiple is {bm['value']}x (target <2x). Cash consumption relative to "
            "growth is unsustainable. Prioritize operating efficiency and path to profitability."
        )

    # Rule of 40
    r40 = metrics["rule_of_40"]
    if r40["rating"] == "Red":
        recs.append(
            f"Rule of 40 score is {r40['value']}% (target >40%). Balance of growth and "
            "profitability needs improvement. Either accelerate growth or improve margins."
        )

    # NDR
    ndr = metrics["ndr"]
    if ndr["rating"] == "Red":
        recs.append(
            f"NDR is {ndr['ndr_pct']}% (target >110%). Net revenue is contracting from "
            "the existing base. Prioritize churn reduction and expansion playbooks."
        )
    elif ndr["rating"] == "Yellow":
        recs.append(
            f"NDR is {ndr['ndr_pct']}%. Base is stable but not expanding. "
            "Invest in cross-sell/upsell motions and customer success capacity."
        )

    # Positive summary if everything is green
    green_count = sum(
        1 for m in metrics.values()
        if isinstance(m, dict) and m.get("rating") == "Green"
    )
    total_metrics = 6
    if green_count == total_metrics:
        recs.append(
            "All GTM efficiency metrics are in healthy ranges. Maintain current "
            "trajectory and optimize for best-in-class performance."
        )
    elif green_count >= 4:
        recs.append(
            f"{green_count}/{total_metrics} metrics are green. GTM efficiency is generally "
            "healthy. Address the yellow/red areas for continuous improvement."
        )

    return recs

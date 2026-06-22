# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gtm_efficiency_calculator_base import *  # noqa: F403,E402
# fmt: off
from gtm_efficiency_calculator_p5 import format_currency  # noqa: E402,E501
# fmt: on


def format_text_report(results: dict) -> str:
    """Format analysis results as a human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("GTM EFFICIENCY REPORT")
    lines.append("=" * 70)

    # Metric summary table
    metrics_order = [
        ("magic_number", "Magic Number", lambda m: f"{m['value']}"),
        ("ltv_cac", "LTV:CAC Ratio", lambda m: f"{m['ratio']}:1"),
        ("cac_payback", "CAC Payback", lambda m: f"{m['months']} months"),
        ("burn_multiple", "Burn Multiple", lambda m: f"{m['value']}x"),
        ("rule_of_40", "Rule of 40", lambda m: f"{m['value']}%"),
        ("ndr", "Net Dollar Retention", lambda m: f"{m['ndr_pct']}%"),
    ]

    lines.append("")
    lines.append("METRICS SUMMARY")
    lines.append("-" * 70)
    lines.append(f"  {'Metric':25s} {'Value':>12s} {'Rating':>8s} {'Target':>15s}")
    lines.append(f"  {'':25s} {'':>12s} {'':>8s} {'':>15s}")

    for key, name, fmt_fn in metrics_order:
        m = results[key]
        lines.append(
            f"  {name:25s} {fmt_fn(m):>12s} {m['rating']:>8s} {m['target']:>15s}"
        )

    # Detailed breakdown
    lines.append("")
    lines.append("DETAILED BREAKDOWN")
    lines.append("-" * 70)

    # Magic Number
    mn = results["magic_number"]
    lines.append("")
    lines.append(f"  MAGIC NUMBER: {mn['value']}")
    lines.append(f"    Net New ARR:         {format_currency(mn['net_new_arr'])}")
    lines.append(f"    S&M Spend:           {format_currency(mn['sm_spend'])}")
    lines.append(f"    Rating:              {mn['rating']} - {mn['label']}")
    lines.append(f"    Percentile:          {mn['percentile']}")

    # LTV:CAC
    lc = results["ltv_cac"]
    lines.append("")
    lines.append(f"  LTV:CAC RATIO: {lc['ratio']}:1")
    lines.append(f"    Customer LTV:        {format_currency(lc['ltv'])}")
    lines.append(f"    CAC:                 {format_currency(lc['cac'])}")
    lines.append(f"    ARPA (Monthly):      {format_currency(lc['arpa_monthly'])}")
    lines.append(f"    Gross Margin:        {lc['gross_margin_pct']}%")
    lines.append(f"    Churn Rate:          {lc['annual_churn_rate_pct']}%")
    lines.append(f"    Rating:              {lc['rating']} - {lc['label']}")
    lines.append(f"    Percentile:          {lc['percentile']}")

    # CAC Payback
    cp = results["cac_payback"]
    lines.append("")
    lines.append(f"  CAC PAYBACK: {cp['months']} months")
    lines.append(f"    CAC:                 {format_currency(cp['cac'])}")
    lines.append(f"    Monthly Contribution:{format_currency(cp['monthly_contribution'])}")
    lines.append(f"    Rating:              {cp['rating']} - {cp['label']}")
    lines.append(f"    Percentile:          {cp['percentile']}")

    # Burn Multiple
    bm = results["burn_multiple"]
    lines.append("")
    lines.append(f"  BURN MULTIPLE: {bm['value']}x")
    lines.append(f"    Net Burn:            {format_currency(bm['net_burn'])}")
    lines.append(f"    Net New ARR:         {format_currency(bm['net_new_arr'])}")
    lines.append(f"    Rating:              {bm['rating']} - {bm['label']}")
    lines.append(f"    Percentile:          {bm['percentile']}")

    # Rule of 40
    r40 = results["rule_of_40"]
    lines.append("")
    lines.append(f"  RULE OF 40: {r40['value']}%")
    lines.append(f"    Revenue Growth:      {r40['revenue_growth_pct']}%")
    lines.append(f"    FCF Margin:          {r40['fcf_margin_pct']}%")
    lines.append(f"    Rating:              {r40['rating']} - {r40['label']}")
    lines.append(f"    Percentile:          {r40['percentile']}")

    # NDR
    ndr = results["ndr"]
    lines.append("")
    lines.append(f"  NET DOLLAR RETENTION: {ndr['ndr_pct']}%")
    lines.append(f"    Beginning ARR:       {format_currency(ndr['beginning_arr'])}")
    lines.append(f"    Expansion:           +{format_currency(ndr['expansion_arr'])}")
    lines.append(f"    Contraction:         -{format_currency(ndr['contraction_arr'])}")
    lines.append(f"    Churn:               -{format_currency(ndr['churned_arr'])}")
    lines.append(f"    Ending ARR:          {format_currency(ndr['ending_arr'])}")
    lines.append(f"    Rating:              {ndr['rating']} - {ndr['label']}")
    lines.append(f"    Percentile:          {ndr['percentile']}")

    # Recommendations
    lines.append("")
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 70)
    for i, rec in enumerate(results["recommendations"], 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)

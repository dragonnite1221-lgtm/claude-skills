# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402


def prioritize_risks(risks: list[dict], budget: Optional[float] = None) -> list[dict]:
    """Return risks sorted by ALE. If budget given, show what fits."""
    sorted_risks = sorted(risks, key=lambda r: -r["ale"])
    if budget is None:
        return sorted_risks

    # Greedy budget allocation by ROI
    actionable = [r for r in sorted_risks if r["mitigation_status"] in ("None", "Planned")
                  and r["mitigation_cost"] > 0]
    actionable.sort(key=lambda r: -r["mitigation_roi_pct"])

    allocated = []
    remaining = budget
    for risk in actionable:
        if risk["mitigation_cost"] <= remaining:
            allocated.append(risk)
            remaining -= risk["mitigation_cost"]

    return allocated
def fmt_dollars(amount: float) -> str:
    """Format a dollar amount."""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:.0f}"
def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"
def severity_label(ale: float) -> str:
    if ale >= 200_000:
        return "CRITICAL"
    if ale >= 75_000:
        return "HIGH"
    if ale >= 25_000:
        return "MEDIUM"
    return "LOW"
def severity_color(label: str) -> str:
    """ANSI color codes."""
    colors = {
        "CRITICAL": "\033[91m",  # Red
        "HIGH": "\033[93m",      # Yellow
        "MEDIUM": "\033[94m",    # Blue
        "LOW": "\033[92m",       # Green
    }
    return colors.get(label, "") + label + "\033[0m"
def print_header():
    print("\n" + "=" * 80)
    print("  CISO RISK QUANTIFIER — Security Risk Portfolio")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)
def print_portfolio_summary(summary: dict):
    print("\n📊 PORTFOLIO SUMMARY")
    print("-" * 60)
    print(f"  Total risks tracked:          {summary['total_risks']}")
    print(f"  Total inherent ALE:           {fmt_dollars(summary['total_inherent_ale'])}/yr")
    print(f"  Total ALE after mitigations:  {fmt_dollars(summary['total_mitigated_ale'])}/yr")
    print(f"  Risk reduction from controls: {fmt_dollars(summary['total_risk_reduction'])}/yr")
    print(f"  Total mitigation spend:       {fmt_dollars(summary['total_mitigation_cost'])}/yr")
    print(f"  Portfolio ROI:                {fmt_pct(summary['portfolio_roi_pct'])}")
    print()

    print("  Risk by Category (sorted by ALE):")
    for cat, data in summary["by_category"].items():
        print(f"    {cat:<35} {data['count']} risks  ALE: {fmt_dollars(data['total_ale'])}/yr")

    print()
    print("  Mitigation Status:")
    for status, count in summary["by_mitigation_status"].items():
        print(f"    {status:<20} {count} risks")
def print_risk_table(risks: list[dict], title: str = "RISK REGISTER"):
    print(f"\n🎯 {title}")
    print("-" * 80)
    header = f"{'#':<3} {'Risk Name':<35} {'Severity':<10} {'ALE/yr':<12} {'Mitig Cost':<12} {'ROI':<8} {'Status':<12}"
    print(header)
    print("-" * 80)

    for i, risk in enumerate(risks, 1):
        sev = severity_label(risk["ale"])
        sev_str = sev.ljust(10)
        roi = fmt_pct(risk["mitigation_roi_pct"]) if risk["mitigation_cost"] > 0 else "N/A"
        print(
            f"{i:<3} {risk['name'][:34]:<35} {sev_str} "
            f"{fmt_dollars(risk['ale']):<12} {fmt_dollars(risk['mitigation_cost']):<12} "
            f"{roi:<8} {risk['mitigation_status']}"
        )
def print_risk_detail(risk: dict, index: int):
    sev = severity_label(risk["ale"])
    print(f"\n{'─' * 70}")
    print(f"  #{index} — {risk['name']}  [{sev}]")
    print(f"{'─' * 70}")
    print(f"  Category:    {risk['category']}")
    print(f"  Description: {risk['description'][:120]}...")
    print()
    print(f"  RISK CALCULATION:")
    print(f"    Asset Value:             {fmt_dollars(risk['asset_value'])}")
    print(f"    Exposure Factor:         {fmt_pct(risk['exposure_factor'] * 100)}")
    print(f"    Single Loss Expectancy:  {fmt_dollars(risk['sle'])}")
    print(f"    Annual Rate (ARO):       {risk['annual_rate']:.2f}x/year")
    print(f"    Annual Loss Expectancy:  {fmt_dollars(risk['ale'])}/yr  ← INHERENT RISK")
    print()
    print(f"  MITIGATION:")
    print(f"    Mitigation Cost:         {fmt_dollars(risk['mitigation_cost'])}/yr")
    print(f"    Effectiveness:           {fmt_pct(risk['mitigation_effectiveness'] * 100)}")
    print(f"    Residual ALE:            {fmt_dollars(risk['mitigated_ale'])}/yr")
    print(f"    Mitigation ROI:          {fmt_pct(risk['mitigation_roi_pct'])}")
    print(f"    Status:                  {risk['mitigation_status']}")
    print()
    print(f"  BUSINESS IMPACT BREAKDOWN:")
    for impact_type, amount in risk["business_impacts"].items():
        print(f"    {impact_type:<30} {fmt_dollars(amount)}")
    print(f"    {'TOTAL':<30} {fmt_dollars(risk['total_business_impact'])}")
    if risk["notes"]:
        print(f"\n  NOTES: {risk['notes']}")

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402
# fmt: off
from risk_quantifier_p1 import BUSINESS_IMPACT_TYPES, MITIGATION_STATUSES, RISK_CATEGORIES, build_risk  # noqa: E402,E501
from risk_quantifier_p4 import fmt_dollars, fmt_pct, severity_label  # noqa: E402,E501
# fmt: on


def print_board_summary(risks: list[dict], summary: dict):
    """One-page board-ready summary."""
    print("\n" + "═" * 80)
    print("  BOARD SECURITY REPORT — Risk Summary")
    print("═" * 80)

    critical = [r for r in risks if severity_label(r["ale"]) == "CRITICAL"]
    high = [r for r in risks if severity_label(r["ale"]) == "HIGH"]
    medium = [r for r in risks if severity_label(r["ale"]) == "MEDIUM"]
    low = [r for r in risks if severity_label(r["ale"]) == "LOW"]

    print(f"\n  RISK EXPOSURE SUMMARY")
    print(f"  ┌─────────────┬────────┬──────────────┐")
    print(f"  │ Severity    │ Count  │ Total ALE/yr │")
    print(f"  ├─────────────┼────────┼──────────────┤")
    for label, group in [("Critical", critical), ("High", high), ("Medium", medium), ("Low", low)]:
        ale = sum(r["ale"] for r in group)
        print(f"  │ {label:<11} │ {len(group):<6} │ {fmt_dollars(ale):<12} │")
    print(f"  └─────────────┴────────┴──────────────┘")

    print(f"\n  TOTAL INHERENT RISK:   {fmt_dollars(summary['total_inherent_ale'])}/yr")
    print(f"  SECURITY INVESTMENT:   {fmt_dollars(summary['total_mitigation_cost'])}/yr")
    print(f"  RESIDUAL RISK:         {fmt_dollars(summary['total_mitigated_ale'])}/yr")
    print(f"  RISK REDUCTION:        {fmt_dollars(summary['total_risk_reduction'])}/yr")
    print(f"  PORTFOLIO ROI:         {fmt_pct(summary['portfolio_roi_pct'])}")

    print(f"\n  TOP 3 RISKS BY EXPECTED ANNUAL LOSS:")
    top3 = sorted(risks, key=lambda r: -r["ale"])[:3]
    for i, risk in enumerate(top3, 1):
        print(f"    {i}. {risk['name']}: {fmt_dollars(risk['ale'])}/yr expected annual loss")
        print(f"       Mitigation: {fmt_dollars(risk['mitigation_cost'])}/yr | "
              f"Status: {risk['mitigation_status']}")

    unmitigated = [r for r in risks if r["mitigation_status"] == "None"]
    if unmitigated:
        print(f"\n  ⚠️  UNMITIGATED RISKS ({len(unmitigated)}):")
        for r in sorted(unmitigated, key=lambda x: -x["ale"]):
            print(f"    • {r['name']}: {fmt_dollars(r['ale'])}/yr — Action required")
def export_csv(risks: list[dict], filepath: str):
    fields = [
        "name", "category", "asset_value", "exposure_factor", "annual_rate",
        "sle", "ale", "mitigation_cost", "mitigation_effectiveness",
        "mitigated_ale", "mitigation_roi_pct", "mitigation_status", "notes"
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for risk in risks:
            row = {k: risk.get(k, "") for k in fields}
            writer.writerow(row)
    print(f"✅ Exported {len(risks)} risks to {filepath}")
def export_json(risks: list[dict]) -> str:
    return json.dumps(risks, indent=2, default=str)
def interactive_add_risk() -> dict:
    """Interactive CLI for adding a new risk."""
    print("\n── ADD NEW RISK ──────────────────────────────────────")
    name = input("Risk name: ").strip()

    print(f"Category options: {', '.join(RISK_CATEGORIES)}")
    category = input("Category: ").strip()

    description = input("Description (brief): ").strip()

    print("\nAsset valuation:")
    asset_value = float(input("  Asset value ($): ").replace(",", "").replace("$", ""))
    exposure_factor = float(input("  Exposure factor (0.0–1.0, fraction of value lost): "))
    annual_rate = float(input("  Annual rate of occurrence (e.g., 0.10 = once per 10 years): "))

    print("\nMitigation:")
    mitigation_cost = float(input("  Mitigation cost ($/yr): ").replace(",", "").replace("$", ""))
    mitigation_effectiveness = float(input("  Mitigation effectiveness (0.0–1.0): "))

    print(f"Status options: {', '.join(MITIGATION_STATUSES)}")
    mitigation_status = input("  Status: ").strip()

    print("\nBusiness impacts (enter 0 to skip):")
    business_impacts = {}
    for impact_type in BUSINESS_IMPACT_TYPES:
        val = input(f"  {impact_type} ($): ").replace(",", "").replace("$", "")
        amount = float(val) if val else 0
        if amount > 0:
            business_impacts[impact_type] = amount

    notes = input("\nNotes: ").strip()

    return build_risk(
        name=name,
        category=category,
        description=description,
        asset_value=asset_value,
        exposure_factor=exposure_factor,
        annual_rate=annual_rate,
        mitigation_cost=mitigation_cost,
        mitigation_effectiveness=mitigation_effectiveness,
        mitigation_status=mitigation_status,
        business_impacts=business_impacts,
        notes=notes,
    )

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402
# fmt: off
from risk_quantifier_p3 import calculate_portfolio_summary, load_sample_risks  # noqa: E402,E501
from risk_quantifier_p4 import fmt_dollars, fmt_pct, print_header, print_portfolio_summary, print_risk_detail, print_risk_table, prioritize_risks  # noqa: E402,E501
from risk_quantifier_p5 import export_csv, interactive_add_risk, print_board_summary  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="CISO Risk Quantifier — Quantify security risks in business terms"
    )
    parser.add_argument("--json", action="store_true", help="Output full JSON")
    parser.add_argument("--csv", metavar="FILE", help="Export CSV to file")
    parser.add_argument("--budget", type=float, metavar="DOLLARS",
                        help="Show recommended mitigations within budget")
    parser.add_argument("--board", action="store_true", help="Show board-ready summary only")
    parser.add_argument("--detail", action="store_true", help="Show detailed risk breakdowns")
    parser.add_argument("--add", action="store_true", help="Interactively add a risk")
    args = parser.parse_args()

    risks = load_sample_risks()

    if args.add:
        new_risk = interactive_add_risk()
        risks.append(new_risk)
        print(f"\n✅ Added risk: {new_risk['name']} | ALE: {fmt_dollars(new_risk['ale'])}/yr")

    # Sort by ALE descending
    risks_sorted = sorted(risks, key=lambda r: -r["ale"])
    summary = calculate_portfolio_summary(risks_sorted)

    if args.json:
        output = {
            "generated": datetime.now().isoformat(),
            "summary": summary,
            "risks": risks_sorted,
        }
        print(json.dumps(output, indent=2, default=str))
        return

    if args.csv:
        export_csv(risks_sorted, args.csv)
        return

    print_header()

    if args.board:
        print_board_summary(risks_sorted, summary)
        return

    print_portfolio_summary(summary)
    print_risk_table(risks_sorted)

    if args.detail:
        for i, risk in enumerate(risks_sorted, 1):
            print_risk_detail(risk, i)

    if args.budget:
        recommended = prioritize_risks(risks_sorted, args.budget)
        print(f"\n💰 BUDGET ALLOCATION — ${args.budget:,.0f}")
        print(f"   Recommended mitigations (sorted by ROI):")
        if recommended:
            for r in recommended:
                print(f"   • {r['name']}: {fmt_dollars(r['mitigation_cost'])}/yr "
                      f"| ALE reduction: {fmt_dollars(r['ale'] - r['mitigated_ale'])}/yr "
                      f"| ROI: {fmt_pct(r['mitigation_roi_pct'])}")
        else:
            print("   No actionable mitigations fit within budget.")

    print_board_summary(risks_sorted, summary)

    print("\n💡 NEXT STEPS")
    print("   1. Run `--detail` to see full breakdown of each risk")
    print("   2. Run `--budget 200000` to see what you can mitigate with a given budget")
    print("   3. Run `--board` for a board-ready one-page summary")
    print("   4. Run `--csv risks.csv` to export for stakeholder review")
    print("   5. Run `--add` to interactively add risks to the register")
    print()

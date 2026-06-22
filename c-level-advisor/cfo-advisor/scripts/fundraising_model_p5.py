# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fundraising_model_base import *  # noqa: F403,E402
# fmt: off
from fundraising_model_p3 import export_csv_rounds, fmt, print_dilution_summary, print_exit_analysis, print_round_result  # noqa: E402,E501
from fundraising_model_p4 import build_sample_model  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(description="Fundraising Model — Cap Table & Dilution")
    parser.add_argument("--exit", type=float, default=250.0,
                        help="Exit valuation in $M for return analysis (default: 250)")
    parser.add_argument("--csv", action="store_true", help="Export round data as CSV to stdout")
    args = parser.parse_args()

    exit_valuation = args.exit * 1_000_000

    print("\n" + "="*70)
    print("  FUNDRAISING MODEL — CAP TABLE & DILUTION ANALYSIS")
    print("  Sample Company: Two-founder SaaS startup")
    print("  Pre-seed → Seed → Series A → Series B → Series C")
    print("="*70)

    cap, rounds = build_sample_model()

    # Print each round
    prev = None
    for r in rounds:
        print_round_result(r, prev)
        prev = r.cap_table

    # Dilution summary table
    print_dilution_summary(rounds)

    # Exit analysis at specified valuation
    exit_results = cap.analyze_exit(exit_valuation)
    print_exit_analysis(exit_results, exit_valuation)

    # Also print at 2x and 5x for sensitivity
    print("\n  Exit Sensitivity — Founder A Proceeds:")
    print(f"  {'Exit Valuation':<20} {'Founder A %':>12} {'Founder A $':>14} {'MOIC':>8}")
    print("  " + "-"*56)
    for mult in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
        val = rounds[-1].post_money_valuation * mult
        ex = cap.analyze_exit(val)
        founder_a = next((r for r in ex if r.shareholder == "Founder A (CEO)"), None)
        if founder_a:
            print(f"  {fmt(val):<20} {founder_a.ownership_pct*100:>11.2f}% "
                  f"{fmt(founder_a.proceeds_common):>14}  {'n/a':>8}")

    print("\n  Key Takeaways:")
    final = rounds[-1].cap_table
    total = sum(e.shares for e in final)
    founder_a_final = next((e for e in final if e.name == "Founder A (CEO)"), None)
    if founder_a_final:
        print(f"    Founder A final ownership: {founder_a_final.pct_ownership*100:.2f}%")
    total_raised = sum(e.invested for e in final)
    print(f"    Total capital raised:      {fmt(total_raised)}")
    print(f"    Total shares outstanding:  {total:,.0f}")
    print(f"    Final post-money:          {fmt(rounds[-1].post_money_valuation)}")
    print("\n    Run with --exit <$M> to model proceeds at different exit valuations.")
    print("    Example: python fundraising_model.py --exit 500")

    if args.csv:
        print("\n\n--- CSV EXPORT ---\n")
        sys.stdout.write(export_csv_rounds(rounds))

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from burn_rate_calculator_base import *  # noqa: F403,E402
# fmt: off
from burn_rate_calculator_p1 import MonthResult  # noqa: E402,E501
from burn_rate_calculator_p2 import RunwayCalculator  # noqa: E402,E501
from burn_rate_calculator_p3 import export_csv, make_sample_configs, print_monthly_table, print_summary  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(description="Startup Burn Rate & Runway Calculator")
    parser.add_argument("--csv", action="store_true", help="Export full monthly data as CSV to stdout")
    parser.add_argument("--scenario", choices=["bull", "base", "bear", "distress", "all"], default="all")
    args = parser.parse_args()

    configs = make_sample_configs()
    if args.scenario != "all":
        configs = [c for c in configs if args.scenario.upper() in c.name.upper()]

    all_results: list[tuple[str, list[MonthResult]]] = []

    print("\n" + "="*60)
    print("  BURN RATE & RUNWAY CALCULATOR")
    print("  Sample Company: Series A SaaS Startup")
    print("  Starting cash: $3M | Starting MRR: $125K | 18 employees")
    print("="*60)

    for cfg in configs:
        calc = RunwayCalculator(cfg)
        results = calc.run()
        all_results.append((cfg.name, results))
        print_summary(cfg.name, results, calc)
        print_monthly_table(results)

    # Comparison summary
    print("\n" + "="*60)
    print("  SCENARIO COMPARISON")
    print("="*60)
    print(f"  {'Scenario':<40} {'Runway':>8} {'Cash Out':<30} {'Burn Mult':>10}")
    print("  " + "-"*88)
    for cfg, (name, results) in zip(configs, all_results):
        calc = RunwayCalculator(cfg)
        cash_out = calc.cash_out_date(results) or "Survives model period"
        bm = calc.burn_multiple(results)
        final_runway = results[-1].runway_months
        runway_str = f"{final_runway:.1f}mo" if final_runway != float("inf") else "∞"
        bm_str = f"{bm:.2f}x" if bm != float("inf") else "∞"
        print(f"  {name:<40} {runway_str:>8} {cash_out:<30} {bm_str:>10}")

    print("\n  Decision Trigger Reference:")
    print("    9 months runway → Start fundraise process")
    print("    6 months runway → Begin cost reduction planning")
    print("    4 months runway → Execute cuts; explore bridge financing")
    print("    3 months runway → Emergency plan only")

    if args.csv:
        print("\n\n--- CSV EXPORT ---\n")
        sys.stdout.write(export_csv(all_results))

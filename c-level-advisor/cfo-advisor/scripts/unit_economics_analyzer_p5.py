# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_analyzer_base import *  # noqa: F403,E402
# fmt: off
from unit_economics_analyzer_p2 import analyze_channel, analyze_cohort, fmt  # noqa: E402,E501
from unit_economics_analyzer_p3 import export_csv_results, print_channel_analysis, print_cohort_analysis, rating  # noqa: E402,E501
from unit_economics_analyzer_p4 import make_sample_channels, make_sample_cohorts  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(description="Unit Economics Analyzer")
    parser.add_argument("--csv", action="store_true", help="Export results as CSV to stdout")
    args = parser.parse_args()

    cohorts = make_sample_cohorts()
    channels = make_sample_channels()

    print("\n" + "="*80)
    print("  UNIT ECONOMICS ANALYZER")
    print("  Sample Company: Series A SaaS | Q4 2024 Snapshot")
    print("  Gross Margin: ~72% | Monthly Churn: derived from cohort data")
    print("="*80)

    cohort_results = [analyze_cohort(c) for c in cohorts]
    channel_results = [analyze_channel(c) for c in channels]

    print_cohort_analysis(cohort_results)
    print_channel_analysis(channel_results, channels)

    # Health summary
    print("\n" + "="*80)
    print("  HEALTH SUMMARY")
    print("="*80)
    latest = cohort_results[-1]
    prev = cohort_results[-4] if len(cohort_results) >= 4 else cohort_results[0]

    print(f"\n  Latest Cohort ({latest.label}):")
    print(f"    CAC:          {fmt(latest.cac)}")
    ltv_str = fmt(latest.ltv) if latest.ltv != float("inf") else "∞"
    ltv_cac_str = f"{latest.ltv_cac_ratio:.1f}x" if latest.ltv_cac_ratio != float("inf") else "∞"
    payback_str = f"{latest.payback_months:.1f} months" if latest.payback_months != float("inf") else "∞"
    print(f"    LTV:          {ltv_str}")
    print(f"    LTV:CAC:      {ltv_cac_str}  (target: > 3x)")
    print(f"    CAC Payback:  {payback_str}  (target: < 18mo)")
    print(f"    Rating:       {rating(latest.ltv_cac_ratio, latest.payback_months)}")

    # Trend vs 4 quarters ago
    print(f"\n  Trend vs {prev.label}:")
    cac_delta = (latest.cac - prev.cac) / prev.cac * 100
    ltv_delta_str = "n/a"
    if latest.ltv != float("inf") and prev.ltv != float("inf"):
        ltv_delta = (latest.ltv - prev.ltv) / prev.ltv * 100
        ltv_delta_str = f"{ltv_delta:+.1f}%"
    cac_str = "↓ Better" if cac_delta < 0 else "↑ Worse"
    print(f"    CAC:    {cac_delta:+.1f}%  ({cac_str})")
    print(f"    LTV:    {ltv_delta_str}")

    print("\n  Benchmark Reference:")
    print("    LTV:CAC > 5x  → Scale aggressively")
    print("    LTV:CAC 3-5x  → Healthy; grow at current pace")
    print("    LTV:CAC 2-3x  → Marginal; optimize before scaling")
    print("    LTV:CAC < 2x  → Acquiring unprofitably; stop and fix")
    print("    Payback < 12mo → Outstanding capital efficiency")
    print("    Payback 12-18mo → Good for B2B SaaS")
    print("    Payback > 24mo → Requires long-dated capital to scale")

    if args.csv:
        print("\n\n--- CSV EXPORT ---\n")
        sys.stdout.write(export_csv_results(cohort_results, channel_results))

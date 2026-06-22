# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_analyzer_p2 import RetentionAnalyzer  # noqa: E402,E501
from churn_analyzer_p3 import CohortAnalyzer  # noqa: E402,E501
from churn_analyzer_p4 import ExpansionAnalyzer, fmt_currency, fmt_pct, grr_status, nrr_status, print_header  # noqa: E402,E501
from churn_analyzer_p5 import print_full_report  # noqa: E402,E501
from churn_analyzer_p6 import SAMPLE_CSV, load_customers_from_csv, parse_period  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Churn & Retention Analyzer — NRR, cohort analysis, at-risk detection"
    )
    parser.add_argument(
        "--csv", metavar="FILE",
        help="CSV file with customer data (uses sample data if not provided)"
    )
    parser.add_argument(
        "--period", metavar="PERIOD",
        help='Analysis period: "2026-Q1" or "2026-03" (defaults to current quarter)'
    )
    parser.add_argument(
        "--output", choices=["summary", "full", "json"],
        default="full",
        help="Output format (default: full)"
    )
    args = parser.parse_args()

    # Load data
    if args.csv:
        try:
            with open(args.csv, "r", encoding="utf-8") as f:
                csv_text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.csv}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No --csv provided. Using sample customer data.\n")
        csv_text = SAMPLE_CSV

    customers = load_customers_from_csv(csv_text)
    if not customers:
        print("No customers loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    period_start, period_end = parse_period(args.period)

    if args.output == "json":
        analyzer = RetentionAnalyzer(customers, as_of=period_end)
        cohort_analyzer = CohortAnalyzer(customers)
        expansion_analyzer = ExpansionAnalyzer(customers)
        wf = analyzer.arr_waterfall(period_start, period_end)
        output = {
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "arr_waterfall": wf,
            "logo_churn_rate": analyzer.logo_churn_rate(period_start, period_end),
            "revenue_churn_rate": analyzer.revenue_churn_rate(period_start, period_end),
            "cohort_report": {k: {**v, "retention_curve": {str(m): r for m, r in v["retention_curve"].items()}}
                              for k, v in cohort_analyzer.cohort_report().items()},
            "at_risk_accounts": cohort_analyzer.identify_at_risk(),
            "expansion_summary": expansion_analyzer.expansion_summary(),
            "expansion_by_segment": expansion_analyzer.expansion_by_segment(),
            "expansion_candidates": expansion_analyzer.top_expansion_candidates(),
        }
        print(json.dumps(output, indent=2))
    elif args.output == "summary":
        analyzer = RetentionAnalyzer(customers, as_of=period_end)
        wf = analyzer.arr_waterfall(period_start, period_end)
        print_header("NRR SUMMARY")
        print(f"  Period:  {period_start.isoformat()} → {period_end.isoformat()}")
        print(f"  NRR:     {fmt_pct(wf['nrr'])}  {nrr_status(wf['nrr'])}")
        print(f"  GRR:     {fmt_pct(wf['grr'])}  {grr_status(wf['grr'])}")
        print(f"  Opening: {fmt_currency(wf['opening_arr'])}")
        print(f"  Closing: {fmt_currency(wf['closing_arr'])}")
        print(f"  Net New: {fmt_currency(wf['net_new_arr'])}")
        print()
    else:
        print_full_report(customers, period_start, period_end)

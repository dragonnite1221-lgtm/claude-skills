# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from revenue_forecast_model_base import *  # noqa: F403,E402
# fmt: off
from revenue_forecast_model_p1 import DEFAULT_STAGE_PROBABILITIES, Deal, calculate_historical_win_rates  # noqa: E402,E501
from revenue_forecast_model_p2 import ForecastEngine  # noqa: E402,E501
from revenue_forecast_model_p4 import print_report  # noqa: E402,E501
# fmt: on


SAMPLE_CSV = """deal_id,name,stage,arr_value,close_date,rep,segment
D001,Acme Corp ERP Integration,negotiation,85000,2026-03-15,Sarah Chen,Enterprise
D002,TechStart PLG Expansion,proposal,28000,2026-03-28,Marcus Webb,Mid-Market
D003,Global Retail Co,verbal_commit,220000,2026-03-10,Sarah Chen,Enterprise
D004,BioLab Analytics,poc,62000,2026-04-05,Jamie Park,Mid-Market
D005,FinServ Holdings,demo,150000,2026-04-20,Sarah Chen,Enterprise
D006,MidWest Logistics,qualification,35000,2026-04-30,Marcus Webb,Mid-Market
D007,Edu Platform Inc,negotiation,42000,2026-03-25,Jamie Park,SMB
D008,Healthcare Connect,proposal,95000,2026-05-15,Sarah Chen,Enterprise
D009,Startup Hub Network,demo,18000,2026-04-10,Marcus Webb,SMB
D010,CloudOps Systems,poc,75000,2026-05-01,Jamie Park,Mid-Market
D011,National Bank Corp,verbal_commit,310000,2026-03-31,Sarah Chen,Enterprise
D012,RetailTech Co,qualification,22000,2026-05-20,Marcus Webb,SMB
D013,InsurTech Platform,negotiation,88000,2026-04-15,Jamie Park,Mid-Market
D014,GovTech Solutions,proposal,175000,2026-06-01,Sarah Chen,Enterprise
D015,AgriData Systems,demo,31000,2026-05-10,Marcus Webb,Mid-Market
D016,Legal AI Corp,poc,55000,2026-04-25,Jamie Park,Mid-Market
D017,Closed Won Deal,closed_won,120000,2026-02-15,Sarah Chen,Enterprise
D018,Lost Deal,closed_lost,45000,2026-02-20,Marcus Webb,Mid-Market
"""
def load_deals_from_csv(csv_text):
    reader = csv.DictReader(StringIO(csv_text))
    deals = []
    errors = []
    for i, row in enumerate(reader, start=2):
        try:
            deal = Deal(
                deal_id=row.get("deal_id", f"row_{i}"),
                name=row.get("name", ""),
                stage=row.get("stage", ""),
                arr_value=row.get("arr_value", 0),
                close_date=row.get("close_date", ""),
                rep=row.get("rep", ""),
                segment=row.get("segment", ""),
            )
            deals.append(deal)
        except (ValueError, KeyError) as e:
            errors.append(f"  Row {i}: {e}")
    if errors:
        print("⚠️  Skipped rows with errors:")
        for err in errors:
            print(err)
    return deals
def main():
    parser = argparse.ArgumentParser(
        description="Revenue Forecast Model — pipeline-based ARR forecasting"
    )
    parser.add_argument(
        "--csv", metavar="FILE",
        help="CSV file with pipeline data (uses sample data if not provided)"
    )
    parser.add_argument(
        "--quota", type=float, default=1_000_000,
        help="Quarterly quota target in ARR (default: $1,000,000)"
    )
    parser.add_argument(
        "--quarter", metavar="QUARTER",
        help='Current quarter filter e.g. "Q2 2026" (optional)'
    )
    parser.add_argument(
        "--scenario", choices=["conservative", "base", "upside"],
        default="base",
        help="Primary scenario to report (default: base)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output forecast as JSON instead of formatted report"
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
        print("No --csv provided. Using sample pipeline data.\n")
        csv_text = SAMPLE_CSV

    deals = load_deals_from_csv(csv_text)
    if not deals:
        print("No deals loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Calibrate win rates from closed deals
    historical_probs = calculate_historical_win_rates(deals)
    stage_probs = historical_probs if historical_probs else DEFAULT_STAGE_PROBABILITIES

    engine = ForecastEngine(deals, stage_probs=stage_probs)

    if args.json:
        output = {
            "generated": date.today().isoformat(),
            "quota": args.quota,
            "open_pipeline": sum(d.arr_value for d in engine.open_deals()),
            "coverage_ratio": engine.coverage_ratio(args.quota, args.quarter),
            "monthly_forecast": engine.scenario_summary(),
            "quarterly_base": engine.pipeline_by_quarter("base"),
            "confidence_interval": dict(zip(
                ["p10", "p50", "p90"],
                engine.confidence_interval("base")
            )),
            "rep_performance": engine.rep_performance(),
            "segment_breakdown": engine.segment_breakdown("base"),
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(engine, quota=args.quota, current_quarter=args.quarter)

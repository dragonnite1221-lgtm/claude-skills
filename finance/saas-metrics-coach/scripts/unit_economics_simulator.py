# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_simulator_base import *  # noqa: F403,E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulate SaaS unit economics over 12 months"
    )
    parser.add_argument("--mrr", type=float, required=True, help="Starting MRR")
    parser.add_argument(
        "--growth", type=float, required=True, help="Monthly growth rate (pct)"
    )
    parser.add_argument(
        "--churn", type=float, required=True, help="Monthly churn rate (pct)"
    )
    parser.add_argument("--cac", type=float, required=True, help="Customer acquisition cost")
    parser.add_argument(
        "--gross-margin", type=float, default=70, help="Gross margin %% (default: 70)"
    )
    parser.add_argument(
        "--sm-spend", type=float, default=30, help="S&M spend as %% of revenue (default: 30)"
    )
    parser.add_argument(
        "--months", type=int, default=12, help="Months to project (default: 12)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    results = simulate(
        mrr=args.mrr,
        monthly_growth_pct=args.growth,
        monthly_churn_pct=args.churn,
        cac=args.cac,
        gross_margin=args.gross_margin / 100 if args.gross_margin > 1 else args.gross_margin,
        sm_spend_pct=args.sm_spend / 100 if args.sm_spend > 1 else args.sm_spend,
        months=args.months,
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))

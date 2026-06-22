# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from roas_calculator_base import *  # noqa: F403,E402
# fmt: off
from roas_calculator_p2 import DEMO_DATA, calculate  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="ROAS calculator — paid ads performance metrics and recommendations."
    )
    parser.add_argument("--spend",       type=float, help="Total ad spend ($)")
    parser.add_argument("--revenue",     type=float, default=0, help="Total attributed revenue ($)")
    parser.add_argument("--conversions", type=int,   default=0, help="Number of purchases/conversions")
    parser.add_argument("--leads",       type=int,   default=0, help="Number of leads generated")
    parser.add_argument("--margin",      type=float, default=0, help="Gross margin %% (e.g. 40)")
    parser.add_argument("--impressions", type=int,   default=0, help="Total impressions")
    parser.add_argument("--clicks",      type=int,   default=0, help="Total clicks")
    parser.add_argument("--file",        help="JSON file with campaign data")
    parser.add_argument("--json",        action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            data = json.load(f)
    elif args.spend:
        data = {
            "spend": args.spend,
            "revenue": args.revenue,
            "conversions": args.conversions,
            "leads": args.leads,
            "margin_pct": args.margin,
            "impressions": args.impressions,
            "clicks": args.clicks,
        }
    else:
        data = DEMO_DATA
        if not args.json:
            print("No input provided — running in demo mode.\n")

    result = calculate(
        spend=data.get("spend", 0),
        revenue=data.get("revenue", 0),
        conversions=data.get("conversions", 0),
        leads=data.get("leads", 0),
        margin_pct=data.get("margin_pct", 0),
        impressions=data.get("impressions", 0),
        clicks=data.get("clicks", 0),
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    inp = result["inputs"]
    metrics = result["metrics"]
    recs = result["recommendations"]

    print("=" * 62)
    print("  PAID ADS PERFORMANCE REPORT")
    print("=" * 62)
    print(f"  Spend:      ${inp['ad_spend']:>10,.2f}")
    if inp["revenue"]:    print(f"  Revenue:    ${inp['revenue']:>10,.2f}")
    if inp["conversions"]:print(f"  Conversions:{inp['conversions']:>10}")
    if inp["leads"]:      print(f"  Leads:      {inp['leads']:>10}")
    if inp["impressions"]:print(f"  Impressions:{inp['impressions']:>10,}")
    if inp["clicks"]:     print(f"  Clicks:     {inp['clicks']:>10,}")

    print()
    print("  METRICS")
    print("  " + "─" * 58)

    metric_labels = [
        ("roas",                   "ROAS",                    lambda m: f"{m['value']}x  — {m['interpretation']}"),
        ("break_even_roas",        "Break-even ROAS",         lambda m: f"{m['value']}x  — {m['note']}"),
        ("profitability",          "Profitability",           lambda m: m['note']),
        ("cpa",                    "CPA",                     lambda m: f"${m['value']:,.2f} / {m['unit']}"),
        ("revenue_per_conversion", "Rev/Conversion",          lambda m: f"${m['value']:,.2f}  (ROI {m['roi_per_conversion']}%)"),
        ("cpl",                    "CPL",                     lambda m: f"${m['value']:,.2f} / {m['unit']}"),
        ("lead_to_conversion_rate","Lead→Conv Rate",          lambda m: f"{m['value']}%"),
        ("conversion_rate",        "Conversion Rate",         lambda m: f"{m['value']}%  ({m['benchmark']})"),
        ("ctr",                    "CTR",                     lambda m: f"{m['value']}%"),
        ("cpc",                    "CPC",                     lambda m: f"${m['value']:,.2f}"),
        ("cpm",                    "CPM",                     lambda m: f"${m['value']:,.2f}"),
    ]

    for key, label, fmt in metric_labels:
        if key in metrics:
            try:
                detail = fmt(metrics[key])
                print(f"  {label:<24} {detail}")
            except Exception:
                pass

    print()
    print("  RECOMMENDATIONS")
    print("  " + "─" * 58)
    for rec in recs:
        print(f"  {rec}")
    print("=" * 62)

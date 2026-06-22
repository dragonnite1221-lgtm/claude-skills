# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_roi_estimator_base import *  # noqa: F403,E402
# fmt: off
from tool_roi_estimator_p1 import build_projection, calculate_minimum_traffic, find_break_even_month  # noqa: E402,E501
from tool_roi_estimator_p2 import calculate_roi_summary, print_report  # noqa: E402,E501
# fmt: on


DEFAULT_PARAMS = {
    "tool_name": "SaaS ROI Calculator",
    "build_cost": 4000,
    "monthly_maintenance": 100,
    "traffic_month_1": 600,
    "traffic_growth_rate": 0.12,
    "seo_ramp_months": 3,
    "tool_completion_rate": 0.55,
    "lead_capture_rate": 0.12,
    "lead_to_trial_rate": 0.08,
    "trial_to_paid_rate": 0.25,
    "ltv": 1400,
    "months_to_model": 18,
    "backlink_value_monthly": 150,
}
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Estimates ROI of building a free marketing tool. "
                    "Models return given build cost, maintenance, traffic, "
                    "conversion rate, and lead value."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a JSON file with tool parameters. "
             "If omitted, reads from stdin or runs embedded sample."
    )
    args = parser.parse_args()

    params = None

    if args.file:
        try:
            with open(args.file) as f:
                params = json.load(f)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            try:
                params = json.loads(raw)
            except Exception as e:
                print(f"Error reading stdin: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("No input provided — running with sample parameters.\n")
            params = DEFAULT_PARAMS
    else:
        print("No input provided — running with sample parameters.\n")
        params = DEFAULT_PARAMS

    # Fill defaults for any missing keys
    for k, v in DEFAULT_PARAMS.items():
        params.setdefault(k, v)

    projection = build_projection(params)
    summary = calculate_roi_summary(projection, params)
    break_even = find_break_even_month(projection)
    min_traffic = calculate_minimum_traffic(params)

    print_report(params, projection, summary, break_even, min_traffic)

    # JSON output
    json_output = {
        "inputs": params,
        "results": {
            "roi_pct": summary["roi_pct"],
            "break_even_month": break_even,
            "total_leads": summary["total_leads"],
            "total_customers": summary["total_customers"],
            "cost_per_lead": summary["cost_per_lead"],
            "net_benefit": summary["net_benefit"],
            "min_monthly_traffic_for_12mo_breakeven": min_traffic,
        }
    }

    print("\n--- JSON Output ---")
    print(json.dumps(json_output, indent=2))

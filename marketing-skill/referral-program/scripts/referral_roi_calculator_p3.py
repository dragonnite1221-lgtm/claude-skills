# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from referral_roi_calculator_base import *  # noqa: F403,E402
# fmt: off
from referral_roi_calculator_p1 import calculate_break_even_referral_rate, calculate_cac_via_referral, calculate_monthly_program_cost, calculate_optimal_reward, calculate_referrals_per_month, calculate_roi  # noqa: E402,E501
from referral_roi_calculator_p2 import build_monthly_projection, find_break_even_month, print_report  # noqa: E402,E501
# fmt: on


DEFAULT_PARAMS = {
    "ltv": 1200,
    "cac": 350,
    "active_users": 800,
    "referral_rate": 0.06,
    "referrals_per_referrer": 2.0,
    "referral_conversion_rate": 0.20,
    "referrer_reward": 50,
    "referred_reward": 30,
    "program_overhead_monthly": 200,
    "churn_rate_monthly": 0.04,
    "months_to_model": 12,
}
def run(params):
    monthly = calculate_referrals_per_month(params)
    new_customers = monthly["new_customers_per_month"]
    costs = calculate_monthly_program_cost(params, new_customers)
    cac = calculate_cac_via_referral(costs, new_customers)
    break_even_rate = calculate_break_even_referral_rate(params)
    optimal_reward = calculate_optimal_reward(params)
    roi = calculate_roi(params)
    projection = build_monthly_projection(params)
    break_even_month = find_break_even_month(projection)

    results = {
        "monthly_referrals": monthly,
        "monthly_costs": costs,
        "cac_via_referral": cac,
        "break_even_referral_rate": break_even_rate,
        "optimal_reward": optimal_reward,
        "roi": roi,
        "monthly_projection": projection,
        "break_even_month": break_even_month,
    }

    return results
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculates referral program ROI. "
                    "Models economics given LTV, CAC, referral rate, reward cost, "
                    "and conversion rate."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a JSON file with referral program parameters. "
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

    # Fill in defaults for any missing keys
    for k, v in DEFAULT_PARAMS.items():
        params.setdefault(k, v)

    results = run(params)
    print_report(params, results)

    # JSON output
    json_output = {
        "inputs": params,
        "results": {
            "monthly_new_customers": results["monthly_referrals"]["new_customers_per_month"],
            "cac_via_referral": results["cac_via_referral"],
            "program_roi_pct": results["roi"]["roi_pct"],
            "break_even_month": results["break_even_month"],
            "break_even_referral_rate": results["break_even_referral_rate"],
            "optimal_total_reward": results["optimal_reward"]["max_total_reward"],
            "net_benefit_12mo": results["roi"]["net_benefit"],
        }
    }

    print("\n--- JSON Output ---")
    print(json.dumps(json_output, indent=2))

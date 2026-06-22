# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pricing_modeler_base import *  # noqa: F403,E402
# fmt: off
from pricing_modeler_p1 import SAMPLE_INPUT, calculate_arpu, elasticity_estimate, project_revenue_at_price, recommend_tier_structure  # noqa: E402,E501
from pricing_modeler_p2 import print_report  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pricing modeler — projects revenue at different price points and recommends tier structure."
    )
    parser.add_argument(
        "input_file", nargs="?", default=None,
        help="JSON file with pricing data (default: run with sample data)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file) as f:
            inputs = json.load(f)
    else:
        if not args.json:
            print("No input file provided. Running with sample data...\n")
        inputs = SAMPLE_INPUT

    current_arpu = calculate_arpu(inputs["current_plans"])
    total_customers = inputs["current_customers"]
    cogs = inputs["cogs_per_customer_monthly"]
    target_margin = inputs["target_gross_margin_pct"]

    gross_margin = ((current_arpu - cogs) / current_arpu * 100) if current_arpu > 0 else 0

    tier_rec = recommend_tier_structure(
        inputs["current_plans"],
        inputs.get("competitor_prices", []),
        cogs,
        target_margin
    )

    elast = elasticity_estimate(inputs["trial_to_paid_rate_pct"], current_arpu)

    # Model multiple scenarios
    churn = inputs["monthly_churn_rate_pct"]
    new_mo = inputs["monthly_new_customers"]

    scenarios = []
    for label, arpu in [
        ("Current pricing", current_arpu),
        ("5% price increase", current_arpu * 1.05),
        ("15% price increase", current_arpu * 1.15),
        ("25% price increase", current_arpu * 1.25),
        ("Recommended tiers", tier_rec["mid"]["recommended_price"])
    ]:
        proj = project_revenue_at_price(total_customers, current_arpu, arpu, new_mo, churn)
        scenarios.append({"scenario": label, "arpu": round(arpu, 2), **proj})

    result = {
        "current_state": {
            "current_mrr": inputs["current_mrr"],
            "customers": total_customers,
            "arpu": round(current_arpu, 2),
            "gross_margin_pct": round(gross_margin, 1)
        },
        "elasticity": elast,
        "tier_recommendation": tier_rec,
        "price_scenarios": scenarios
    }

    print_report(result, inputs)

    if args.json:
        print(json.dumps(result, indent=2))

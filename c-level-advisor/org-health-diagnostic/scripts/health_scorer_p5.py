# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_scorer_base import *  # noqa: F403,E402
# fmt: off
from health_scorer_p1 import Stage  # noqa: E402,E501
from health_scorer_p2 import build_engineering_dimension, build_financial_dimension, build_operations_dimension, build_people_dimension, build_product_dimension, build_revenue_dimension, build_security_dimension  # noqa: E402,E501
from health_scorer_p3 import build_market_dimension, calculate_overall, print_dashboard  # noqa: E402,E501
from health_scorer_p4 import build_sample_data, interactive_mode, to_json  # noqa: E402,E501
# fmt: on


def main():
    print("\n🏥 ORG HEALTH DIAGNOSTIC")
    print("Multi-dimension organizational health scorer\n")

    # Determine stage
    stage_map = {
        "seed": Stage.SEED, "a": Stage.SERIES_A, "series_a": Stage.SERIES_A,
        "b": Stage.SERIES_B, "series_b": Stage.SERIES_B,
        "c": Stage.SERIES_C, "series_c": Stage.SERIES_C,
    }
    stage_arg = next((a for a in sys.argv[1:] if a.lower() in stage_map), None)
    stage = stage_map.get(stage_arg.lower(), Stage.SERIES_A) if stage_arg else Stage.SERIES_A

    if "--interactive" in sys.argv or "-i" in sys.argv:
        company = input("Company name: ").strip() or "Company"
        stage_input = input("Stage (seed/a/b/c): ").strip().lower()
        stage = stage_map.get(stage_input, Stage.SERIES_A)
        data = interactive_mode(stage)
    else:
        print(f"Running sample Series A company data.")
        print("(Use --interactive or -i for custom data, --stage seed/a/b/c for stage)\n")
        company = "Sample Co"
        data = build_sample_data(stage)

    # Build dimensions
    dimensions = [
        build_financial_dimension(stage, **data),
        build_revenue_dimension(stage, **data),
        build_product_dimension(**data),
        build_engineering_dimension(**data),
        build_people_dimension(stage, **data),
        build_operations_dimension(**data),
        build_security_dimension(**data),
        build_market_dimension(**data),
    ]

    overall = calculate_overall(dimensions, stage)
    print_dashboard(dimensions, overall, stage, company)

    if "--json" in sys.argv:
        print(json.dumps(to_json(dimensions, overall, stage), indent=2))

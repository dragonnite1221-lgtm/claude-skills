# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_plan_modeler_base import *  # noqa: F403,E402
# fmt: off
from hiring_plan_modeler_p1 import HireTarget, HiringPlan  # noqa: E402,E501
from hiring_plan_modeler_p3 import export_csv, print_report  # noqa: E402,E501
from hiring_plan_modeler_p4 import build_sample_plan  # noqa: E402,E501
# fmt: on


def load_plan_from_json(path: str) -> HiringPlan:
    with open(path) as f:
        data = json.load(f)
    hires = [HireTarget(**h) for h in data.pop("hires", [])]
    plan = HiringPlan(**data)
    plan.hires = hires
    return plan
def main():
    parser = argparse.ArgumentParser(
        description="Hiring Plan Modeler — build headcount plans with cost projections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hiring_plan_modeler.py                       # Run sample plan
  python hiring_plan_modeler.py --config plan.json    # Load from JSON
  python hiring_plan_modeler.py --export-csv          # Output CSV of hires
  python hiring_plan_modeler.py --export-json         # Output plan as JSON template
        """
    )
    parser.add_argument("--config", help="Path to JSON plan file")
    parser.add_argument("--export-csv", action="store_true", help="Export hire detail as CSV")
    parser.add_argument("--export-json", action="store_true", help="Export sample plan as JSON template")
    args = parser.parse_args()

    if args.config:
        plan = load_plan_from_json(args.config)
    else:
        plan = build_sample_plan()

    if args.export_json:
        data = asdict(plan)
        print(json.dumps(data, indent=2))
        return

    if args.export_csv:
        print(export_csv(plan))
        return

    print_report(plan)

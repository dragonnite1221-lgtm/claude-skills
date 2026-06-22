# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p7 import _mod_cg0_0, run_analysis  # noqa: E402,E501
from ops_efficiency_analyzer_p8 import _mod_cg0_1  # noqa: E402,E501
# fmt: on


def _mod_cg0_2():
    return {
        "team": {
        "total_headcount": 85,
        "annual_revenue_usd": 18000000,
        "stage": "series_b",
        "management_layers": 3,
        "open_requisitions": 18,
        "departments": [
            {
                "name": "Engineering",
                "headcount": 32,
                "managers": [
                    {"name": "VP Engineering", "direct_reports": 4, "manages_managers": True},
                    {"name": "Engineering Manager (Platform)", "direct_reports": 7, "manages_managers": False},
                    {"name": "Engineering Manager (Product)", "direct_reports": 8, "manages_managers": False},
                    {"name": "Engineering Manager (Infra)", "direct_reports": 9, "manages_managers": False},
                ],
            },
            {
                "name": "Sales",
                "headcount": 18,
                "managers": [
                    {"name": "VP Sales", "direct_reports": 3, "manages_managers": True},
                    {"name": "Sales Manager (SMB)", "direct_reports": 6, "manages_managers": False},
                    {"name": "Sales Manager (Enterprise)", "direct_reports": 4, "manages_managers": False},
                ],
            },
            {
                "name": "Customer Success",
                "headcount": 12,
                "managers": [
                    {"name": "VP CS", "direct_reports": 2, "manages_managers": False},
                ],
            },
            {
                "name": "Marketing",
                "headcount": 8,
                "managers": [
                    {"name": "VP Marketing", "direct_reports": 7, "manages_managers": False},
                ],
            },
            {
                "name": "Operations",
                "headcount": 6,
                "managers": [
                    {"name": "COO", "direct_reports": 5, "manages_managers": True},
                ],
            },
            {
                "name": "Product",
                "headcount": 9,
                "managers": [
                    {"name": "VP Product", "direct_reports": 8, "manages_managers": False},
                ],
            },
        ],
    },
    }
SAMPLE_DATA = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2()}
def main():
    parser = argparse.ArgumentParser(
        description="Operational Efficiency Analyzer — COO Advisor Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON input file (default: use built-in sample data)",
        default=None,
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write report (default: stdout)",
        default=None,
    )
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input file specified — running with sample data.\n")
        data = SAMPLE_DATA

    report = run_analysis(data)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402
# fmt: off
from comp_benchmarker_p1 import BandDefinition, CompRoster, Employee  # noqa: E402,E501
from comp_benchmarker_p3 import print_report  # noqa: E402,E501
from comp_benchmarker_p4 import export_csv  # noqa: E402,E501
from comp_benchmarker_p5 import build_sample_roster  # noqa: E402,E501
# fmt: on


def load_roster_from_json(path: str) -> CompRoster:
    with open(path) as f:
        data = json.load(f)
    employees = [Employee(**e) for e in data.pop("employees", [])]
    bands = [BandDefinition(**b) for b in data.pop("bands", [])]
    roster = CompRoster(**data)
    roster.employees = employees
    roster.bands = bands
    return roster
def main():
    parser = argparse.ArgumentParser(
        description="Compensation Benchmarker — salary analysis and pay equity audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python comp_benchmarker.py                          # Run sample roster
  python comp_benchmarker.py --config roster.json     # Load from JSON
  python comp_benchmarker.py --export-csv             # Output CSV
  python comp_benchmarker.py --export-json            # Output JSON template
        """
    )
    parser.add_argument("--config", help="Path to JSON roster file")
    parser.add_argument("--export-csv", action="store_true", help="Export analysis as CSV")
    parser.add_argument("--export-json", action="store_true", help="Export sample roster as JSON template")
    args = parser.parse_args()

    if args.config:
        roster = load_roster_from_json(args.config)
    else:
        roster = build_sample_roster()

    if args.export_json:
        data = asdict(roster)
        print(json.dumps(data, indent=2))
        return

    if args.export_csv:
        print(export_csv(roster))
        return

    print_report(roster)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from stakeholder_mapper_base import *  # noqa: F403,E402
# fmt: off
from stakeholder_mapper_p3 import print_report  # noqa: E402,E501
from stakeholder_mapper_p4 import SAMPLE_DATA, interactive_mode  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Stakeholder Mapper — influence, alignment, and engagement strategy"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: enter stakeholder data manually"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Load stakeholder data from JSON file"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Print sample JSON structure and exit"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        print(json.dumps(SAMPLE_DATA, indent=2))
        return
    
    if args.interactive:
        interactive_mode()
        return
    
    if args.file:
        try:
            with open(args.file) as f:
                data = json.load(f)
            print_report(data)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.file}': {e}")
            sys.exit(1)
        return
    
    # Default: sample data
    print()
    print("Running with sample data. Use --interactive for custom input or --file for JSON.")
    print_report(SAMPLE_DATA)

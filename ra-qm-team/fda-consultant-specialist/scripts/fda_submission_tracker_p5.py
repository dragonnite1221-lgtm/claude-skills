# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fda_submission_tracker_base import *  # noqa: F403,E402
# fmt: off
from fda_submission_tracker_p3 import generate_sample_config  # noqa: E402,E501
from fda_submission_tracker_p4 import analyze_submission, print_text_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="FDA Submission Tracker - Monitor 510(k), De Novo, and PMA submissions"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--type",
        choices=["510k", "510k_traditional", "510k_special", "510k_abbreviated",
                 "de_novo", "pma", "pma_supplement"],
        help="Submission type (overrides config file)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create sample configuration file"
    )

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    if args.init:
        config_path = project_dir / "fda_submission.json"
        if config_path.exists():
            print(f"Configuration file already exists: {config_path}")
            sys.exit(1)

        sample = generate_sample_config()
        if args.type:
            sample["submission_type"] = args.type

        with open(config_path, "w") as f:
            json.dump(sample, f, indent=2)

        print(f"Created sample configuration: {config_path}")
        print("Edit this file with your submission details and milestone dates.")
        return

    result = analyze_submission(project_dir, args.type)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_text_report(result)

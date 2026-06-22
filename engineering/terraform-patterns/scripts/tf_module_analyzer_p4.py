# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_module_analyzer_base import *  # noqa: F403,E402
# fmt: off
from tf_module_analyzer_p1 import DEMO_FILES, find_tf_files  # noqa: E402,E501
from tf_module_analyzer_p3 import analyze_directory, generate_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="terraform-patterns: Terraform module analyzer"
    )
    parser.add_argument(
        "directory", nargs="?",
        help="Path to Terraform directory (omit for demo)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if args.directory:
        dirpath = Path(args.directory)
        if not dirpath.is_dir():
            print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
            sys.exit(1)
        tf_files = find_tf_files(str(dirpath))
        if not tf_files:
            print(f"Error: No .tf files found in {args.directory}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No directory provided. Running demo analysis...\n")
        tf_files = DEMO_FILES

    analysis = analyze_directory(tf_files)
    generate_report(analysis, args.output)

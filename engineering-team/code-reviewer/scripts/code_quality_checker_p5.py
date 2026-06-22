# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_checker_base import *  # noqa: F403,E402
# fmt: off
from code_quality_checker_p1 import LANGUAGE_EXTENSIONS  # noqa: E402,E501
from code_quality_checker_p3 import analyze_file  # noqa: E402,E501
from code_quality_checker_p4 import analyze_directory, print_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Analyze code quality, smells, and SOLID violations"
    )
    parser.add_argument(
        "path",
        help="File or directory to analyze"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="Recursively analyze directories (default: true)"
    )
    parser.add_argument(
        "--language", "-l",
        choices=list(LANGUAGE_EXTENSIONS.keys()),
        help="Filter by programming language"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file"
    )

    args = parser.parse_args()

    target = Path(args.path).resolve()

    if not target.exists():
        print(f"Error: Path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    if target.is_file():
        analysis = analyze_file(target)
    else:
        analysis = analyze_directory(target, args.recursive, args.language)

    if args.json:
        output = json.dumps(analysis, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
    else:
        print_report(analysis)

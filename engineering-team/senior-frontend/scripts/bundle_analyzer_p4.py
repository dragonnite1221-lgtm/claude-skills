# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from bundle_analyzer_base import *  # noqa: F403,E402
# fmt: off
from bundle_analyzer_p1 import load_package_json  # noqa: E402,E501
from bundle_analyzer_p2 import analyze_dependencies, check_nextjs_config  # noqa: E402,E501
from bundle_analyzer_p3 import analyze_imports, calculate_score, print_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Analyze frontend project for bundle optimization opportunities"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include detailed import analysis"
    )

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    package_json = load_package_json(project_dir)
    if not package_json:
        print("Error: No valid package.json found", file=sys.stderr)
        sys.exit(1)

    analysis = {
        "project": str(project_dir),
        "dependencies": analyze_dependencies(package_json),
        "nextjs": check_nextjs_config(project_dir)
    }

    if args.verbose:
        analysis["imports"] = analyze_imports(project_dir)

    analysis["score"], analysis["grade"] = calculate_score(analysis)

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_report(analysis)

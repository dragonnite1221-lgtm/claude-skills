# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p1 import build_report, format_size  # noqa: E402,E501
# fmt: on


def print_text(report: Dict[str, object]) -> None:
    print("Codebase Onboarding Summary")
    print(f"Root: {report['root']}")
    print(f"Total files: {report['file_count']}")
    print("")

    print("Languages detected")
    if report["languages"]:
        for lang, count in report["languages"].items():
            print(f"- {lang}: {count}")
    else:
        print("- No recognized source file extensions")
    print("")

    print("Key config files")
    configs = report["key_config_files"]
    if configs:
        for cfg in configs:
            print(f"- {cfg}")
    else:
        print("- None found from default checklist")
    print("")

    print("Largest files")
    for rel, size in report["largest_files"][:10]:
        print(f"- {rel}: {format_size(size)}")
    print("")

    print("Directory structure")
    for line in report["directory_structure"][:200]:
        print(line)
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a repository and generate onboarding summary facts.")
    parser.add_argument("path", help="Path to project directory")
    parser.add_argument("--max-depth", type=int, default=2, help="Max depth for structure output (default: 2)")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()
def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Path is not a directory: {root}")

    report = build_report(root, max_depth=max(1, args.max_depth))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0

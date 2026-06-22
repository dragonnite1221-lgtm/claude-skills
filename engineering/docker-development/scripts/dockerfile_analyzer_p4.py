# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dockerfile_analyzer_base import *  # noqa: F403,E402
# fmt: off
from dockerfile_analyzer_p2 import DEMO_DOCKERFILE  # noqa: E402,E501
from dockerfile_analyzer_p3 import generate_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="docker-development: Dockerfile static analyzer"
    )
    parser.add_argument("dockerfile", nargs="?", help="Path to Dockerfile (omit for demo)")
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Security-focused analysis only",
    )
    args = parser.parse_args()

    if args.dockerfile:
        path = Path(args.dockerfile)
        if not path.exists():
            print(f"Error: File not found: {args.dockerfile}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
    else:
        print("No Dockerfile provided. Running demo analysis...\n")
        content = DEMO_DOCKERFILE

    generate_report(content, args.output, args.security)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_report_generator_base import *  # noqa: F403,E402
# fmt: off
from review_report_generator_p1 import load_json_file  # noqa: E402,E501
from review_report_generator_p3 import format_markdown_report  # noqa: E402,E501
from review_report_generator_p4 import format_text_report, generate_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive code review reports"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--pr-analysis",
        help="Path to pre-computed PR analysis JSON"
    )
    parser.add_argument(
        "--quality-analysis",
        help="Path to pre-computed quality analysis JSON"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (shortcut for --format json)"
    )

    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    # Load pre-computed analyses if provided
    pr_analysis = None
    quality_analysis = None

    if args.pr_analysis:
        pr_analysis = load_json_file(args.pr_analysis)
        if not pr_analysis:
            print(f"Warning: Could not load PR analysis from {args.pr_analysis}")

    if args.quality_analysis:
        quality_analysis = load_json_file(args.quality_analysis)
        if not quality_analysis:
            print(f"Warning: Could not load quality analysis from {args.quality_analysis}")

    # Generate report
    report = generate_report(repo_path, pr_analysis, quality_analysis)

    # Format output
    output_format = "json" if args.json else args.format

    if output_format == "json":
        output = json.dumps(report, indent=2)
    elif output_format == "markdown":
        output = format_markdown_report(report)
    else:
        output = format_text_report(report)

    # Write or print output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

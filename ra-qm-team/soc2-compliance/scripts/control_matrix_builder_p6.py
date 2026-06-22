# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from control_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from control_matrix_builder_p5 import VALID_CATEGORIES, build_matrix  # noqa: E402,E501
# fmt: on


def format_markdown(matrix: List[Dict[str, str]]) -> str:
    """Format control matrix as markdown table."""
    lines = ["# SOC 2 Control Matrix", ""]
    lines.append(
        "| Control ID | TSC | Category | Description | Type | Frequency | Evidence | Owner | Status |"
    )
    lines.append(
        "|------------|-----|----------|-------------|------|-----------|----------|-------|--------|"
    )
    for row in matrix:
        lines.append(
            "| {control_id} | {tsc_criteria} | {category} | {description} | {control_type} | {frequency} | {evidence_required} | {owner} | {status} |".format(
                **row
            )
        )
    lines.append("")
    lines.append(f"**Total Controls:** {len(matrix)}")
    return "\n".join(lines)
def format_csv(matrix: List[Dict[str, str]]) -> str:
    """Format control matrix as CSV."""
    output = io.StringIO()
    if not matrix:
        return ""
    writer = csv.DictWriter(output, fieldnames=matrix[0].keys())
    writer.writeheader()
    writer.writerows(matrix)
    return output.getvalue()
def format_json(matrix: List[Dict[str, str]]) -> str:
    """Format control matrix as JSON."""
    return json.dumps({"controls": matrix, "total": len(matrix)}, indent=2)
def main():
    parser = argparse.ArgumentParser(
        description="SOC 2 Control Matrix Builder — generates control matrices from selected Trust Service Criteria categories."
    )
    parser.add_argument(
        "--categories",
        type=str,
        required=True,
        help=f"Comma-separated TSC categories: {','.join(VALID_CATEGORIES)}",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["md", "json", "csv"],
        default="md",
        help="Output format (default: md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Shorthand for --format json",
    )

    args = parser.parse_args()

    # Parse categories
    categories = [c.strip().lower() for c in args.categories.split(",")]
    invalid = [c for c in categories if c not in VALID_CATEGORIES]
    if invalid:
        print(
            f"Error: Invalid categories: {', '.join(invalid)}. Valid options: {', '.join(VALID_CATEGORIES)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Build matrix
    matrix = build_matrix(categories)

    if not matrix:
        print("No controls found for the selected categories.", file=sys.stderr)
        sys.exit(1)

    # Output
    fmt = "json" if args.json else args.format
    if fmt == "md":
        print(format_markdown(matrix))
    elif fmt == "json":
        print(format_json(matrix))
    elif fmt == "csv":
        print(format_csv(matrix))

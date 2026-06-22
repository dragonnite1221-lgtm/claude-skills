# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_extractor_base import *  # noqa: F403,E402
# fmt: off
from test_extractor_p1 import SpecParser  # noqa: E402,E501
from test_extractor_p3 import GENERATORS  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Extract test case stubs from a feature specification.",
        epilog="Example: python test_extractor.py --file spec.md --framework pytest --output tests/test_feature.py",
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to the spec markdown file",
    )
    parser.add_argument(
        "--framework",
        choices=list(GENERATORS.keys()),
        default="pytest",
        help="Target test framework (default: pytest)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_flag",
        help="Output extracted criteria as JSON instead of test code",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(2)

    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        print(f"Error: File is empty: {file_path}", file=sys.stderr)
        sys.exit(2)

    spec_parser = SpecParser(content)
    title = spec_parser.extract_spec_title()
    criteria = spec_parser.extract_acceptance_criteria()
    edge_cases = spec_parser.extract_edge_cases()

    if not criteria and not edge_cases:
        print("Error: No acceptance criteria or edge cases found in spec.", file=sys.stderr)
        sys.exit(2)

    warnings = []
    for ac in criteria:
        if not ac["given"] and not ac["when"]:
            warnings.append(f"{ac['id']}: Could not parse Given/When/Then — check format.")

    if args.json_flag:
        result = {
            "spec_title": title,
            "framework": args.framework,
            "acceptance_criteria": criteria,
            "edge_cases": edge_cases,
            "warnings": warnings,
            "counts": {
                "acceptance_criteria": len(criteria),
                "edge_cases": len(edge_cases),
                "total_test_cases": len(criteria) + len(edge_cases),
            },
        }
        output = json.dumps(result, indent=2)
    else:
        generator_class = GENERATORS[args.framework]
        generator = generator_class()
        output = generator.generate(title, criteria, edge_cases)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        total = len(criteria) + len(edge_cases)
        print(f"Generated {total} test stubs -> {out_path}", file=sys.stderr)
    else:
        print(output)

    if warnings:
        for w in warnings:
            print(f"Warning: {w}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

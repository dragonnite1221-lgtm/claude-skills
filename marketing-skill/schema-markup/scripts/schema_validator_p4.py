# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_validator_base import *  # noqa: F403,E402
# fmt: off
from schema_validator_p1 import JSONLDExtractor  # noqa: E402,E501
from schema_validator_p2 import validate_block  # noqa: E402,E501
from schema_validator_p3 import SAMPLE_HTML, print_report  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extracts and validates JSON-LD structured data from HTML. "
                    "Scores 0-100 per schema block based on required/recommended field coverage."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to an HTML file to validate. "
             "Use '-' to read from stdin. If omitted, runs embedded sample."
    )
    args = parser.parse_args()

    if args.file:
        if args.file == "-":
            html = sys.stdin.read()
        else:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    html = f.read()
            except FileNotFoundError:
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
    else:
        print("No file provided — running on embedded sample HTML.\n")
        html = SAMPLE_HTML

    extractor = JSONLDExtractor()
    extractor.feed(html)

    all_results = []
    for i, block in enumerate(extractor.blocks, start=1):
        results = validate_block(block, i)
        all_results.extend(results)

    print_report(all_results, html)

    # JSON output for programmatic use
    summary = {
        "blocks_found": len(extractor.blocks),
        "schemas_validated": len(all_results),
        "average_score": (sum(r.get("score", 0) for r in all_results) // len(all_results)) if all_results else 0,
        "results": all_results,
    }
    print("\n── JSON Output ──")
    print(json.dumps(summary, indent=2))

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_copy_validator_base import *  # noqa: F403,E402
# fmt: off
from ad_copy_validator_p1 import score_ad  # noqa: E402,E501
from ad_copy_validator_p3 import SAMPLE_ADS, format_report, validate_ad  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validates ad copy against platform specs. "
                    "Checks character counts, rejection triggers, and scores each ad 0-100."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a JSON file containing ad data. "
             "If omitted, reads from stdin or runs embedded sample."
    )
    args = parser.parse_args()

    # Load from file or stdin, else use sample
    ads = None

    if args.file:
        try:
            with open(args.file) as f:
                data = json.load(f)
                ads = data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            try:
                data = json.loads(raw)
                ads = data if isinstance(data, list) else [data]
            except Exception as e:
                print(f"Error reading stdin: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("No input provided — running embedded sample ads.\n")
            ads = SAMPLE_ADS
    else:
        print("No input provided — running embedded sample ads.\n")
        ads = SAMPLE_ADS

    # Aggregate results for JSON output
    results = []
    all_output = []

    for ad in ads:
        char_lines, issues = validate_ad(ad)
        score = score_ad(issues)
        report_text = format_report(ad, char_lines, issues)
        all_output.append(report_text)
        results.append({
            "platform": ad.get("platform"),
            "score": score,
            "issues": {k: v for k, v in issues.items()},
            "passed": score >= 70,
        })

    # Human-readable output
    for block in all_output:
        print(block)

    # Summary
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    passed = sum(1 for r in results if r["passed"])
    print(f"\nSUMMARY: {passed}/{len(results)} ads passed (avg score: {avg_score:.0f}/100)")

    # JSON output to stdout (for programmatic use) — write to separate section
    print("\n--- JSON Output ---")
    print(json.dumps(results, indent=2))

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from values_validator_base import *  # noqa: F403,E402
# fmt: off
from values_validator_p1 import DEMO_VALUES  # noqa: E402,E501
from values_validator_p2 import parse_values, validate_naming  # noqa: E402,E501
from values_validator_p3 import validate_defaults, validate_depth, validate_documentation, validate_secrets  # noqa: E402,E501
# fmt: on


def generate_report(content, output_format="text", strict=False):
    """Generate full validation report."""
    entries = parse_values(content)
    findings = []

    findings.extend(validate_naming(entries))
    findings.extend(validate_documentation(entries))
    findings.extend(validate_defaults(entries))
    findings.extend(validate_secrets(entries))
    findings.extend(validate_depth(entries))

    if strict:
        # Elevate medium to high, low to medium
        for f in findings:
            if f["severity"] == "medium":
                f["severity"] = "high"
            elif f["severity"] == "low":
                f["severity"] = "medium"

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    # Score
    deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2}
    score = max(0, 100 - sum(deductions.get(f["severity"], 0) for f in findings))

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }

    # Stats
    total_keys = len(entries)
    documented = sum(1 for e in entries if e["has_documentation"])
    max_depth = max((e["depth"] for e in entries), default=0)

    result = {
        "score": score,
        "total_keys": total_keys,
        "documented_keys": documented,
        "documentation_coverage": f"{(documented / total_keys * 100):.0f}%" if total_keys > 0 else "N/A",
        "max_depth": max_depth,
        "findings": findings,
        "finding_counts": counts,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Values.yaml Validation Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print(f"  Keys: {total_keys} | Documented: {documented} ({result['documentation_coverage']})")
    print(f"  Max Depth: {max_depth}")
    print()
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  {icon} {f['severity'].upper()} [{f['category']}]")
        print(f"  {f['message']}")
        if f.get("line", 0) > 0:
            print(f"  Line: {f['line']}")
        print(f"  Fix:  {f['fix']}")

    if not findings:
        print("\n  No issues found. Values file looks good.")

    print(f"\n{'=' * 60}\n")
    return result
def main():
    parser = argparse.ArgumentParser(
        description="helm-chart-builder: values.yaml best-practice validator"
    )
    parser.add_argument("valuesfile", nargs="?", help="Path to values.yaml (omit for demo)")
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode — elevate warnings to higher severity",
    )
    args = parser.parse_args()

    if args.valuesfile:
        path = Path(args.valuesfile)
        if not path.exists():
            print(f"Error: File not found: {args.valuesfile}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
    else:
        print("No values file provided. Running demo validation...\n")
        content = DEMO_VALUES

    generate_report(content, args.output, args.strict)

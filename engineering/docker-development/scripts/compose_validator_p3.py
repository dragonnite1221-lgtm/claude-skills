# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compose_validator_base import *  # noqa: F403,E402
# fmt: off
from compose_validator_p1 import DEMO_COMPOSE, parse_yaml_simple  # noqa: E402,E501
from compose_validator_p2 import validate_compose  # noqa: E402,E501
# fmt: on


def generate_report(content, output_format="text", strict=False):
    """Generate validation report."""
    parsed = parse_yaml_simple(content)
    findings = validate_compose(parsed, strict)
    services = parsed.get("services", {})

    # Score
    deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2}
    score = max(0, 100 - sum(deductions.get(f["severity"], 0) for f in findings))

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }

    result = {
        "score": score,
        "services": list(services.keys()),
        "service_count": len(services),
        "findings": findings,
        "finding_counts": counts,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Docker Compose Validation Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print(f"  Services: {', '.join(services.keys()) if services else 'none'}")
    print()
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  {icon} {f['severity'].upper()} [{f['category']}] — {f['service']}")
        print(f"  {f['message']}")

    if not findings:
        print("\n  No issues found. Compose file looks good.")

    print(f"\n{'=' * 60}\n")
    return result
def main():
    parser = argparse.ArgumentParser(
        description="docker-development: Docker Compose validator"
    )
    parser.add_argument("composefile", nargs="?", help="Path to docker-compose.yml (omit for demo)")
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

    if args.composefile:
        path = Path(args.composefile)
        if not path.exists():
            print(f"Error: File not found: {args.composefile}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
    else:
        print("No compose file provided. Running demo validation...\n")
        content = DEMO_COMPOSE

    generate_report(content, args.output, args.strict)

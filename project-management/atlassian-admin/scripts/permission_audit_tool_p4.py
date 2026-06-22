# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from permission_audit_tool_base import *  # noqa: F403,E402
# fmt: off
from permission_audit_tool_p3 import audit_permissions  # noqa: E402,E501
# fmt: on


def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("PERMISSION AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    if "error" in result:
        lines.append(f"ERROR: {result['error']}")
        return "\n".join(lines)

    lines.append("AUDIT SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Risk Score: {result['risk_score']}/100 (lower is better)")
    lines.append(f"Health Score: {result['health_score']}/100")
    lines.append(f"Grade: {result['grade'].title()}")
    lines.append(f"Schemes Analyzed: {result['schemes_analyzed']}")
    lines.append("")

    summary = result.get("summary", {})
    lines.append("FINDINGS BY SEVERITY")
    lines.append("-" * 30)
    lines.append(f"Critical: {summary.get('critical', 0)}")
    lines.append(f"High: {summary.get('high', 0)}")
    lines.append(f"Medium: {summary.get('medium', 0)}")
    lines.append(f"Low: {summary.get('low', 0)}")
    lines.append(f"Info: {summary.get('info', 0)}")
    lines.append("")

    findings = result.get("findings", [])
    if findings:
        lines.append("DETAILED FINDINGS")
        lines.append("-" * 30)
        for i, finding in enumerate(findings, 1):
            severity = finding["severity"].upper()
            lines.append(f"{i}. [{severity}] {finding['message']}")
            lines.append(f"   Rule: {finding['rule']}")
            if finding.get("scheme"):
                lines.append(f"   Scheme: {finding['scheme']}")
            lines.append("")

    remediations = result.get("remediations", [])
    if remediations:
        lines.append("REMEDIATION RECOMMENDATIONS")
        lines.append("-" * 30)
        for i, rem in enumerate(remediations, 1):
            lines.append(f"{i}. {rem}")

    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result
def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit Atlassian permission schemes for security issues"
    )
    parser.add_argument(
        "permissions_file",
        help="JSON file with permission scheme data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    try:
        with open(args.permissions_file, "r") as f:
            data = json.load(f)

        result = audit_permissions(data)

        if args.format == "json":
            print(json.dumps(format_json_output(result), indent=2))
        else:
            print(format_text_output(result))

        return 0

    except FileNotFoundError:
        print(f"Error: File '{args.permissions_file}' not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.permissions_file}': {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

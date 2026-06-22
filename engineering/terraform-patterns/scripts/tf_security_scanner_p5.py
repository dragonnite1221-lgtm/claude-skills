# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_security_scanner_base import *  # noqa: F403,E402
# fmt: off
from tf_security_scanner_p1 import DEMO_TF, SECRET_PATTERNS  # noqa: E402,E501
from tf_security_scanner_p2 import ACCESS_PATTERNS, IAM_PATTERNS, check_regex_rules, find_tf_files  # noqa: E402,E501
from tf_security_scanner_p3 import check_security_groups  # noqa: E402,E501
from tf_security_scanner_p4 import check_encryption, check_sensitive_variables  # noqa: E402,E501
# fmt: on


def scan_content(content, strict=False):
    """Run all security checks on content."""
    findings = []

    findings.extend(check_regex_rules(content, SECRET_PATTERNS))
    findings.extend(check_regex_rules(content, IAM_PATTERNS))
    findings.extend(check_regex_rules(content, ACCESS_PATTERNS))
    findings.extend(check_security_groups(content))
    findings.extend(check_encryption(content))
    findings.extend(check_sensitive_variables(content))

    if strict:
        for f in findings:
            if f["severity"] == "medium":
                f["severity"] = "high"
            elif f["severity"] == "low":
                f["severity"] = "medium"

    # Deduplicate by (id, line)
    seen = set()
    unique = []
    for f in findings:
        key = (f["id"], f.get("line", ""))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    findings = unique

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    return findings
def generate_report(content, output_format="text", strict=False):
    """Generate security scan report."""
    findings = scan_content(content, strict)

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
        "findings": findings,
        "finding_counts": counts,
        "total_findings": len(findings),
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Terraform Security Scan Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print()
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  [{f['id']}] {icon} {f['severity'].upper()}")
        print(f"  {f['message']}")
        if f.get("line"):
            print(f"  Match: {f['line']}")
        print(f"  Fix:   {f['fix']}")

    if not findings:
        print("\n  No security issues found. Configuration looks clean.")

    print(f"\n{'=' * 60}\n")
    return result
def main():
    parser = argparse.ArgumentParser(
        description="terraform-patterns: Terraform security scanner"
    )
    parser.add_argument(
        "target", nargs="?",
        help="Path to Terraform directory or .tf file (omit for demo)",
    )
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

    if args.target:
        target = Path(args.target)
        if target.is_dir():
            tf_files = find_tf_files(str(target))
            if not tf_files:
                print(f"Error: No .tf files found in {args.target}", file=sys.stderr)
                sys.exit(1)
            content = "\n".join(tf_files.values())
        elif target.is_file() and target.suffix == ".tf":
            content = target.read_text(encoding="utf-8")
        else:
            print(f"Error: {args.target} is not a directory or .tf file", file=sys.stderr)
            sys.exit(1)
    else:
        print("No target provided. Running demo scan...\n")
        content = DEMO_TF

    generate_report(content, args.output, args.strict)

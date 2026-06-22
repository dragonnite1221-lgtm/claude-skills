# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gdpr_compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from gdpr_compliance_checker_p1 import CODE_PATTERNS, CONFIG_PATTERNS, PERSONAL_DATA_PATTERNS, SCANNABLE_EXTENSIONS  # noqa: E402,E501
from gdpr_compliance_checker_p2 import generate_recommendations, scan_file_for_patterns, should_skip  # noqa: E402,E501
# fmt: on


def analyze_project(project_path: Path) -> Dict:
    """Analyze project for GDPR compliance issues."""
    personal_data_findings = []
    code_issue_findings = []
    config_findings = []
    files_scanned = 0

    # Scan all relevant files
    for filepath in project_path.rglob("*"):
        if filepath.is_file() and not should_skip(filepath):
            if filepath.suffix.lower() in SCANNABLE_EXTENSIONS:
                files_scanned += 1

                # Check for personal data patterns
                personal_data_findings.extend(
                    scan_file_for_patterns(filepath, PERSONAL_DATA_PATTERNS)
                )

                # Check for code issues
                code_issue_findings.extend(
                    scan_file_for_patterns(filepath, CODE_PATTERNS)
                )

    # Check for specific config files
    for config_name, config_info in CONFIG_PATTERNS.items():
        for config_file in config_info["files"]:
            config_path = project_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        content = f.read()
                    if config_info["check"] not in content.lower():
                        config_findings.append({
                            "file": str(config_path),
                            "config": config_name,
                            "issue": config_info["issue"],
                            "gdpr_article": config_info["gdpr_article"]
                        })
                except Exception:
                    pass

    # Calculate risk scores
    critical_count = sum(1 for f in personal_data_findings if f.get("risk") == "critical")
    critical_count += sum(1 for f in code_issue_findings if f.get("severity") == "critical")

    high_count = sum(1 for f in personal_data_findings if f.get("risk") == "high")
    high_count += sum(1 for f in code_issue_findings if f.get("severity") == "high")

    medium_count = sum(1 for f in personal_data_findings if f.get("risk") == "medium")
    medium_count += sum(1 for f in code_issue_findings if f.get("severity") == "medium")

    # Determine compliance score (100 = compliant, 0 = critical issues)
    score = 100
    score -= critical_count * 20
    score -= high_count * 10
    score -= medium_count * 5
    score -= len(config_findings) * 5
    score = max(0, score)

    # Determine compliance status
    if score >= 80:
        status = "compliant"
        status_description = "Low risk - minor improvements recommended"
    elif score >= 60:
        status = "needs_attention"
        status_description = "Medium risk - action required"
    elif score >= 40:
        status = "non_compliant"
        status_description = "High risk - immediate action required"
    else:
        status = "critical"
        status_description = "Critical risk - significant GDPR violations detected"

    return {
        "summary": {
            "files_scanned": files_scanned,
            "compliance_score": score,
            "status": status,
            "status_description": status_description,
            "issue_counts": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "config_issues": len(config_findings)
            }
        },
        "personal_data_findings": personal_data_findings[:50],  # Limit output
        "code_issues": code_issue_findings[:50],
        "config_issues": config_findings,
        "recommendations": generate_recommendations(
            personal_data_findings, code_issue_findings, config_findings
        )
    }
def print_report(analysis: Dict) -> None:
    """Print human-readable report."""
    summary = analysis["summary"]

    print("=" * 60)
    print("GDPR COMPLIANCE ASSESSMENT REPORT")
    print("=" * 60)
    print()
    print(f"Compliance Score: {summary['compliance_score']}/100")
    print(f"Status: {summary['status'].upper()}")
    print(f"Assessment: {summary['status_description']}")
    print(f"Files Scanned: {summary['files_scanned']}")
    print()

    counts = summary["issue_counts"]
    print("--- ISSUE SUMMARY ---")
    print(f"  Critical: {counts['critical']}")
    print(f"  High: {counts['high']}")
    print(f"  Medium: {counts['medium']}")
    print(f"  Config Issues: {counts['config_issues']}")
    print()

    if analysis["recommendations"]:
        print("--- PRIORITIZED RECOMMENDATIONS ---")
        for i, rec in enumerate(analysis["recommendations"][:10], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['issue']}")
            print(f"   GDPR Article: {rec['gdpr_article']}")
            print(f"   Action: {rec['action']}")

    print()
    print("=" * 60)
    print("Note: This is an automated assessment. Manual review by a")
    print("qualified Data Protection Officer is recommended.")
    print("=" * 60)

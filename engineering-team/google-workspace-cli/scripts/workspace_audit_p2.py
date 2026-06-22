# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workspace_audit_base import *  # noqa: F403,E402
# fmt: off
from workspace_audit_p1 import AuditFinding, AuditReport, DEMO_FINDINGS, audit_drive, run_gws_command  # noqa: E402,E501
# fmt: on


def audit_gmail() -> List[AuditFinding]:
    """Audit Gmail forwarding and email security."""
    findings = []

    # Check forwarding rules
    output = run_gws_command(["gws", "gmail", "users.settings.forwardingAddresses", "list", "me", "--json"])
    if output:
        try:
            data = json.loads(output)
            addrs = data if isinstance(data, list) else data.get("forwardingAddresses", [])
            if addrs:
                findings.append(AuditFinding(
                    "gmail", "Auto-forwarding", "WARN",
                    f"{len(addrs)} forwarding addresses configured",
                    "Data exfiltration via email forwarding",
                    "Review: gws gmail users.settings.forwardingAddresses list me --json"
                ))
            else:
                findings.append(AuditFinding(
                    "gmail", "Auto-forwarding", "PASS",
                    "No forwarding addresses configured"
                ))
        except json.JSONDecodeError:
            pass
    else:
        findings.append(AuditFinding(
            "gmail", "Auto-forwarding", "WARN",
            "Could not check forwarding settings"
        ))

    return findings
def audit_calendar() -> List[AuditFinding]:
    """Audit Calendar sharing settings."""
    findings = []

    output = run_gws_command(["gws", "calendar", "calendarList", "get", "primary", "--json"])
    if output:
        findings.append(AuditFinding(
            "calendar", "Primary calendar", "PASS",
            "Primary calendar accessible"
        ))
    else:
        findings.append(AuditFinding(
            "calendar", "Primary calendar", "WARN",
            "Could not access primary calendar"
        ))

    return findings
def calculate_score(report: AuditReport) -> AuditReport:
    """Calculate audit score and grade."""
    total = len(report.findings)
    if total == 0:
        report.score = 0
        report.grade = "N/A"
        report.summary = "No checks performed"
        return report

    passes = sum(1 for f in report.findings if f["status"] == "PASS")
    warns = sum(1 for f in report.findings if f["status"] == "WARN")
    fails = sum(1 for f in report.findings if f["status"] == "FAIL")

    # Score: PASS=100, WARN=50, FAIL=0
    score = int(((passes * 100) + (warns * 50)) / total)
    report.score = score
    report.max_score = 100

    if score >= 90:
        report.grade = "A"
    elif score >= 75:
        report.grade = "B"
    elif score >= 60:
        report.grade = "C"
    elif score >= 40:
        report.grade = "D"
    else:
        report.grade = "F"

    report.summary = f"{passes} passed, {warns} warnings, {fails} failures — Score: {score}/100 (Grade: {report.grade})"
    return report
def run_live_audit(services: List[str]) -> AuditReport:
    """Run live audit against actual gws installation."""
    report = AuditReport()
    all_findings = []

    audit_map = {
        "drive": audit_drive,
        "gmail": audit_gmail,
        "calendar": audit_calendar,
    }

    for svc in services:
        fn = audit_map.get(svc)
        if fn:
            all_findings.extend(fn())

    report.findings = [asdict(f) for f in all_findings]
    report = calculate_score(report)
    return report
def run_demo_audit() -> AuditReport:
    """Return demo audit report with embedded sample data."""
    report = AuditReport(
        findings=[asdict(f) for f in DEMO_FINDINGS],
        demo_mode=True,
    )
    report = calculate_score(report)
    return report

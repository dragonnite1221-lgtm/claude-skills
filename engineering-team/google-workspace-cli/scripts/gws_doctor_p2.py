# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_doctor_base import *  # noqa: F403,E402
# fmt: off
from gws_doctor_p1 import DEMO_CHECKS, DiagnosticReport, check_auth, check_installation, check_service, check_version  # noqa: E402,E501
# fmt: on


def run_diagnostics(services: List[str]) -> DiagnosticReport:
    """Run all diagnostic checks."""
    report = DiagnosticReport()
    checks = []

    # Installation check
    install_check = check_installation()
    checks.append(install_check)
    report.gws_installed = install_check.status == "PASS"

    if not report.gws_installed:
        report.checks = [asdict(c) for c in checks]
        report.summary = "FAIL: gws is not installed"
        return report

    # Version check
    version_check = check_version()
    checks.append(version_check)
    if version_check.status == "PASS":
        report.gws_version = version_check.message.replace("Version: ", "")

    # Auth check
    auth_check = check_auth()
    checks.append(auth_check)
    report.auth_status = auth_check.status

    if auth_check.status != "PASS":
        report.checks = [asdict(c) for c in checks]
        report.summary = "FAIL: Authentication not configured"
        return report

    # Service checks
    for svc in services:
        checks.append(check_service(svc))

    report.checks = [asdict(c) for c in checks]

    # Summary
    fails = sum(1 for c in checks if c.status == "FAIL")
    warns = sum(1 for c in checks if c.status == "WARN")
    passes = sum(1 for c in checks if c.status == "PASS")
    if fails > 0:
        report.summary = f"ISSUES FOUND: {passes} passed, {warns} warnings, {fails} failures"
    elif warns > 0:
        report.summary = f"MOSTLY OK: {passes} passed, {warns} warnings"
    else:
        report.summary = f"ALL CLEAR: {passes}/{passes} checks passed"

    return report
def run_demo() -> DiagnosticReport:
    """Return demo report with embedded sample data."""
    report = DiagnosticReport(
        gws_installed=True,
        gws_version="0.9.2",
        auth_status="PASS",
        checks=[asdict(c) for c in DEMO_CHECKS],
        summary="MOSTLY OK: 7 passed, 1 warning, 1 failure (demo mode)",
        demo_mode=True,
    )
    return report
def main():
    parser = argparse.ArgumentParser(
        description="Pre-flight diagnostics for Google Workspace CLI (gws)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run all checks
  %(prog)s --json                   # JSON output
  %(prog)s --services gmail,drive   # Check specific services only
  %(prog)s --demo                   # Demo mode (no gws required)
        """,
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--services", default="gmail,drive,calendar,sheets,tasks",
        help="Comma-separated services to check (default: gmail,drive,calendar,sheets,tasks)"
    )
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    services = [s.strip() for s in args.services.split(",") if s.strip()]

    # Use demo mode if requested or gws not installed
    if args.demo or not shutil.which("gws"):
        report = run_demo()
    else:
        report = run_diagnostics(services)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  GWS CLI DIAGNOSTIC REPORT")
        if report.demo_mode:
            print(f"  (DEMO MODE — sample data)")
        print(f"{'='*60}\n")

        for c in report.checks:
            icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}.get(c["status"], "????")
            print(f"  [{icon}] {c['name']}: {c['message']}")
            if c.get("fix") and c["status"] != "PASS":
                print(f"         -> {c['fix']}")

        print(f"\n  {'-'*56}")
        print(f"  {report.summary}")
        print(f"\n{'='*60}\n")

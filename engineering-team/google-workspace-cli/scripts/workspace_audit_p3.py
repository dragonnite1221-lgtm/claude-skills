# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workspace_audit_base import *  # noqa: F403,E402
# fmt: off
from workspace_audit_p2 import run_demo_audit, run_live_audit  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Security and configuration audit for Google Workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Full audit (or demo if gws not installed)
  %(prog)s --json                       # JSON output
  %(prog)s --services gmail,drive       # Audit specific services
  %(prog)s --demo                       # Demo mode with sample data
        """,
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--services", default="gmail,drive,calendar",
                        help="Comma-separated services to audit (default: gmail,drive,calendar)")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    services = [s.strip() for s in args.services.split(",") if s.strip()]

    if args.demo or not shutil.which("gws"):
        report = run_demo_audit()
    else:
        report = run_live_audit(services)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  GOOGLE WORKSPACE SECURITY AUDIT")
        if report.demo_mode:
            print(f"  (DEMO MODE — sample data)")
        print(f"{'='*60}\n")
        print(f"  Score: {report.score}/{report.max_score} (Grade: {report.grade})\n")

        current_area = ""
        for f in report.findings:
            if f["area"] != current_area:
                current_area = f["area"]
                print(f"\n  {current_area.upper()}")
                print(f"  {'-'*40}")

            icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}.get(f["status"], "????")
            print(f"  [{icon}] {f['check']}: {f['message']}")
            if f.get("risk") and f["status"] != "PASS":
                print(f"         Risk: {f['risk']}")
            if f.get("remediation") and f["status"] != "PASS":
                print(f"         Fix: {f['remediation']}")

        print(f"\n  {'='*56}")
        print(f"  {report.summary}")
        print(f"\n{'='*60}\n")

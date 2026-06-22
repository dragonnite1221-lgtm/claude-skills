# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import AuditReport, SEVERITY_LABELS  # noqa: E402,E501
from skill_security_auditor_p9 import clone_repo, scan_skill  # noqa: E402,E501
# fmt: on


def print_report(report: AuditReport):
    """Print formatted audit report to stdout."""
    verdict_symbols = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
    v = report.verdict
    sym = verdict_symbols[v]

    print()
    print("╔" + "═" * 54 + "╗")
    print(f"║  SKILL SECURITY AUDIT REPORT{' ' * 25}║")
    print(f"║  Skill: {report.skill_name:<44} ║")
    print(f"║  Verdict: {sym} {v:<42}║")
    print("╠" + "═" * 54 + "╣")
    print(
        f"║  🔴 CRITICAL: {report.critical_count:<3} "
        f"🟡 HIGH: {report.high_count:<3} "
        f"⚪ INFO: {report.info_count:<3}{' ' * 10}║"
    )
    print(
        f"║  Files: {report.files_scanned}  "
        f"Scripts: {report.scripts_scanned}  "
        f"Markdown: {report.md_files_scanned}{' ' * (17 - len(str(report.files_scanned)) - len(str(report.scripts_scanned)) - len(str(report.md_files_scanned)))}║"
    )
    print("╚" + "═" * 54 + "╝")

    if not report.findings:
        print("\n  No security issues found. Skill is safe to install.\n")
        return

    print()

    # Sort by severity (critical first)
    sorted_findings = sorted(report.findings, key=lambda f: -f.severity)

    for f in sorted_findings:
        label = SEVERITY_LABELS[f.severity]
        loc = f"{f.file}:{f.line}" if f.line > 0 else f.file
        print(f"{label} [{f.category}] {loc}")
        print(f"   Pattern: {f.pattern}")
        print(f"   Risk: {f.risk}")
        print(f"   Fix: {f.fix}")
        print()
def main():
    parser = argparse.ArgumentParser(
        description="Skill Security Auditor — Scan skills for security risks before installation"
    )
    parser.add_argument(
        "path",
        help="Path to skill directory or git repo URL",
    )
    parser.add_argument(
        "--skill",
        help="Skill name within a git repo (subdirectory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode — any WARN becomes FAIL",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON report instead of formatted text",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove cloned repo after audit (only for git URLs)",
    )

    args = parser.parse_args()

    cleanup_dir = None

    # Handle git URLs
    if args.path.startswith(("http://", "https://", "git@")):
        skill_path, cleanup_dir = clone_repo(args.path, args.skill, cleanup=True)
    else:
        skill_path = Path(args.path).resolve()
        if not skill_path.exists():
            print(f"Error: path does not exist: {skill_path}", file=sys.stderr)
            sys.exit(1)
        if not skill_path.is_dir():
            print(f"Error: path is not a directory: {skill_path}", file=sys.stderr)
            sys.exit(1)

    try:
        report = scan_skill(skill_path)

        if args.json_output:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print_report(report)

        # Exit code
        if args.strict and report.verdict == "WARN":
            sys.exit(1)
        elif report.verdict == "FAIL":
            sys.exit(1)
        elif report.verdict == "WARN":
            sys.exit(2)
        else:
            sys.exit(0)

    finally:
        if cleanup_dir:
            shutil.rmtree(cleanup_dir, ignore_errors=True)

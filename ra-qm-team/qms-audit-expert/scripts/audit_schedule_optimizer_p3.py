# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_schedule_optimizer_base import *  # noqa: F403,E402
# fmt: off
from audit_schedule_optimizer_p1 import AuditSchedule, Process, RiskLevel  # noqa: E402,E501
from audit_schedule_optimizer_p2 import AuditScheduleOptimizer  # noqa: E402,E501
# fmt: on


def format_text_output(schedule: AuditSchedule) -> str:
    """Format schedule as text report."""
    lines = [
        "=" * 70,
        "AUDIT SCHEDULE OPTIMIZATION REPORT",
        "=" * 70,
        f"Generated: {schedule.generated_date}",
        f"Period: {schedule.schedule_period}",
        f"Total Audits: {schedule.total_audits}",
        "",
        "Quarterly Distribution:",
    ]

    for q, count in schedule.audits_by_quarter.items():
        bar = "█" * count + "░" * (10 - count)
        lines.append(f"  {q}: {bar} {count}")

    lines.extend([
        "",
        "-" * 70,
        "AUDIT SCHEDULE",
        "-" * 70,
        f"{'Process':<25} {'Clause':<8} {'Date':<12} {'Risk':<8} {'Priority':<8}",
        "-" * 70,
    ])

    for audit in schedule.schedule:
        lines.append(
            f"{audit['process_name']:<25} "
            f"{audit['iso_clause']:<8} "
            f"{audit['scheduled_date']:<12} "
            f"{audit['risk_level']:<8} "
            f"{audit['priority_score']:<8}"
        )

    lines.extend([
        "",
        "-" * 70,
        "RECOMMENDATIONS",
        "-" * 70,
    ])

    for i, rec in enumerate(schedule.recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append("=" * 70)
    return "\n".join(lines)
def interactive_mode():
    """Run interactive schedule generation."""
    print("=" * 60)
    print("Audit Schedule Optimizer - Interactive Mode")
    print("=" * 60)

    processes = []
    print("\nEnter processes (blank name to finish):\n")

    while True:
        name = input("Process name (or Enter to finish): ").strip()
        if not name:
            break

        clause = input("ISO 13485 clause (e.g., 7.3): ").strip()
        risk = input("Risk level (H/M/L): ").strip().upper()
        risk_level = {
            "H": RiskLevel.HIGH,
            "M": RiskLevel.MEDIUM,
            "L": RiskLevel.LOW
        }.get(risk, RiskLevel.MEDIUM)

        last_audit = input("Last audit date (YYYY-MM-DD, or Enter if never): ").strip()
        if not last_audit:
            last_audit = None

        findings = input("Previous findings count (default 0): ").strip()
        findings = int(findings) if findings.isdigit() else 0

        processes.append(Process(
            name=name,
            iso_clause=clause,
            risk_level=risk_level,
            last_audit_date=last_audit,
            previous_findings=findings
        ))

        print(f"Added: {name}\n")

    if not processes:
        print("No processes entered. Using default ISO 13485 processes.")
        processes = [
            Process(name=name, iso_clause=clause, risk_level=RiskLevel.MEDIUM)
            for name, clause in AuditScheduleOptimizer.REQUIRED_PROCESSES
        ]

    optimizer = AuditScheduleOptimizer(processes)
    schedule = optimizer.generate_schedule()
    print("\n" + format_text_output(schedule))

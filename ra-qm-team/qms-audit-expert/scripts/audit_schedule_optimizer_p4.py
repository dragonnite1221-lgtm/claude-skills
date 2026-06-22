# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_schedule_optimizer_base import *  # noqa: F403,E402
# fmt: off
from audit_schedule_optimizer_p1 import Process, RiskLevel  # noqa: E402,E501
from audit_schedule_optimizer_p2 import AuditScheduleOptimizer  # noqa: E402,E501
from audit_schedule_optimizer_p3 import format_text_output, interactive_mode  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Risk-Based Audit Schedule Optimizer"
    )
    parser.add_argument(
        "--processes",
        type=str,
        help="JSON file with process definitions"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=12,
        help="Planning horizon in months"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.processes:
        with open(args.processes, "r") as f:
            data = json.load(f)

        processes = []
        for p in data.get("processes", []):
            risk = RiskLevel[p.get("risk_level", "MEDIUM").upper()]
            processes.append(Process(
                name=p["name"],
                iso_clause=p.get("iso_clause", ""),
                risk_level=risk,
                last_audit_date=p.get("last_audit_date"),
                previous_findings=p.get("previous_findings", 0),
                criticality_score=p.get("criticality_score", 5)
            ))
    else:
        # Use default processes
        processes = [
            Process(name=name, iso_clause=clause, risk_level=RiskLevel.MEDIUM)
            for name, clause in AuditScheduleOptimizer.REQUIRED_PROCESSES
        ]

    optimizer = AuditScheduleOptimizer(processes)
    schedule = optimizer.generate_schedule(args.months)

    if args.output == "json":
        print(json.dumps(asdict(schedule), indent=2))
    else:
        print(format_text_output(schedule))

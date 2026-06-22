# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402
from capa_tracker_p0 import CAPA, CAPASeverity, CAPASource, CAPAStatus  # noqa: F401,E501
from capa_tracker_p1 import format_text_output  # noqa: F401,E501
from capa_tracker_p2 import interactive_mode  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description="CAPA Tracking and Metrics Tool"
    )
    parser.add_argument(
        "--capas",
        type=str,
        help="JSON file with CAPA data"
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
        "--sample",
        action="store_true",
        help="Generate sample CAPA data file"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.sample:
        sample_data = {
            "capas": [
                {
                    "capa_number": "CAPA-2024-001",
                    "title": "Calibration overdue for pH meter",
                    "description": "pH meter EQ-042 found 2 months overdue",
                    "source": "AUDIT",
                    "severity": "MAJOR",
                    "status": "VERIFICATION",
                    "open_date": "2024-06-15",
                    "target_date": "2024-08-15",
                    "owner": "J. Smith",
                    "root_cause": "No trigger for schedule update at equipment purchase",
                    "corrective_action": "Updated SOP-EQ-001 to require schedule update"
                },
                {
                    "capa_number": "CAPA-2024-002",
                    "title": "Customer complaint - labeling error",
                    "description": "Wrong lot number on product label",
                    "source": "COMPLAINT",
                    "severity": "CRITICAL",
                    "status": "INVESTIGATION",
                    "open_date": "2024-09-01",
                    "target_date": "2024-10-01",
                    "owner": "M. Jones"
                },
                {
                    "capa_number": "CAPA-2024-003",
                    "title": "Training records incomplete",
                    "description": "Missing effectiveness verification for 3 operators",
                    "source": "AUDIT",
                    "severity": "MINOR",
                    "status": "CLOSED_EFFECTIVE",
                    "open_date": "2024-03-10",
                    "target_date": "2024-06-10",
                    "owner": "A. Brown",
                    "close_date": "2024-05-20"
                }
            ]
        }
        print(json.dumps(sample_data, indent=2))
        return

    if args.capas:
        with open(args.capas, "r") as f:
            data = json.load(f)

        capas = []
        for c in data.get("capas", []):
            try:
                source = CAPASource[c.get("source", "OTHER").upper()]
            except KeyError:
                source = CAPASource.OTHER

            try:
                severity = CAPASeverity[c.get("severity", "MINOR").upper()]
            except KeyError:
                severity = CAPASeverity.MINOR

            try:
                status = CAPAStatus[c.get("status", "OPEN").upper()]
            except KeyError:
                status = CAPAStatus.OPEN

            capas.append(CAPA(
                capa_number=c["capa_number"],
                title=c.get("title", ""),
                description=c.get("description", ""),
                source=source,
                severity=severity,
                status=status,
                open_date=c["open_date"],
                target_date=c["target_date"],
                owner=c.get("owner", ""),
                root_cause=c.get("root_cause", ""),
                corrective_action=c.get("corrective_action", ""),
                verification_date=c.get("verification_date"),
                close_date=c.get("close_date")
            ))
    else:
        # Demo data if no file provided
        capas = [
            CAPA(
                capa_number="CAPA-2024-001",
                title="Calibration overdue",
                description="pH meter overdue",
                source=CAPASource.AUDIT,
                severity=CAPASeverity.MAJOR,
                status=CAPAStatus.VERIFICATION,
                open_date="2024-06-15",
                target_date="2024-08-15",
                owner="J. Smith"
            ),
            CAPA(
                capa_number="CAPA-2024-002",
                title="Labeling error complaint",
                description="Wrong lot number",
                source=CAPASource.COMPLAINT,
                severity=CAPASeverity.CRITICAL,
                status=CAPAStatus.INVESTIGATION,
                open_date="2024-09-01",
                target_date="2024-10-01",
                owner="M. Jones"
            ),
            CAPA(
                capa_number="CAPA-2024-003",
                title="Training records incomplete",
                description="Missing effectiveness verification",
                source=CAPASource.AUDIT,
                severity=CAPASeverity.MINOR,
                status=CAPAStatus.CLOSED_EFFECTIVE,
                open_date="2024-03-10",
                target_date="2024-06-10",
                owner="A. Brown",
                close_date="2024-05-20"
            )
        ]

    tracker = CAPATracker(capas)
    metrics = tracker.calculate_metrics()
    aging = tracker.get_aging_report()

    if args.output == "json":
        output = {
            "metrics": asdict(metrics),
            "aging": aging
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text_output(metrics, aging))

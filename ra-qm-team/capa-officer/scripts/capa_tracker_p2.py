# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402
from capa_tracker_p0 import CAPA, CAPASeverity, CAPASource, CAPAStatus  # noqa: F401,E501
from capa_tracker_p1 import format_text_output  # noqa: F401,E501


def interactive_mode():
    """Run interactive CAPA entry mode."""
    print("=" * 60)
    print("CAPA Tracker - Interactive Mode")
    print("=" * 60)

    capas = []
    print("\nEnter CAPAs (blank CAPA number to finish):\n")

    while True:
        capa_num = input("CAPA Number (e.g., CAPA-2024-001): ").strip()
        if not capa_num:
            break

        title = input("Title: ").strip()
        description = input("Description: ").strip()

        print("Source options: C=Complaint, A=Audit, N=Nonconformance, M=Management Review, T=Trend, O=Other")
        source_input = input("Source [C/A/N/M/T/O]: ").strip().upper()
        source_map = {
            "C": CAPASource.COMPLAINT,
            "A": CAPASource.AUDIT,
            "N": CAPASource.NONCONFORMANCE,
            "M": CAPASource.MANAGEMENT_REVIEW,
            "T": CAPASource.TREND_ANALYSIS,
            "O": CAPASource.OTHER
        }
        source = source_map.get(source_input, CAPASource.OTHER)

        print("Severity: C=Critical, M=Major, I=Minor")
        severity_input = input("Severity [C/M/I]: ").strip().upper()
        severity_map = {
            "C": CAPASeverity.CRITICAL,
            "M": CAPASeverity.MAJOR,
            "I": CAPASeverity.MINOR
        }
        severity = severity_map.get(severity_input, CAPASeverity.MINOR)

        print("Status: O=Open, I=Investigation, P=Action Planning, M=Implementation, V=Verification, E=Closed Effective, N=Closed Ineffective")
        status_input = input("Status [O/I/P/M/V/E/N]: ").strip().upper()
        status_map = {
            "O": CAPAStatus.OPEN,
            "I": CAPAStatus.INVESTIGATION,
            "P": CAPAStatus.ACTION_PLANNING,
            "M": CAPAStatus.IMPLEMENTATION,
            "V": CAPAStatus.VERIFICATION,
            "E": CAPAStatus.CLOSED_EFFECTIVE,
            "N": CAPAStatus.CLOSED_INEFFECTIVE
        }
        status = status_map.get(status_input, CAPAStatus.OPEN)

        open_date = input("Open Date (YYYY-MM-DD): ").strip()
        target_date = input("Target Date (YYYY-MM-DD): ").strip()
        owner = input("Owner: ").strip()

        close_date = None
        if status in [CAPAStatus.CLOSED_EFFECTIVE, CAPAStatus.CLOSED_INEFFECTIVE]:
            close_date = input("Close Date (YYYY-MM-DD): ").strip()

        capas.append(CAPA(
            capa_number=capa_num,
            title=title,
            description=description,
            source=source,
            severity=severity,
            status=status,
            open_date=open_date,
            target_date=target_date,
            owner=owner,
            close_date=close_date if close_date else None
        ))

        print(f"\nAdded: {capa_num}\n")

    if not capas:
        print("No CAPAs entered. Exiting.")
        return

    tracker = CAPATracker(capas)
    metrics = tracker.calculate_metrics()
    aging = tracker.get_aging_report()
    print("\n" + format_text_output(metrics, aging))

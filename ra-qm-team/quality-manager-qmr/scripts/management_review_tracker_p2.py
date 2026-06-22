# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402
from management_review_tracker_p0 import InputStatus, ManagementReview, ReviewInput, ReviewMetrics  # noqa: F401,E501
from management_review_tracker_p1 import format_text_report  # noqa: F401,E501


def interactive_mode():
    """Run interactive review data entry."""
    print("=" * 60)
    print("Management Review Tracker - Interactive Mode")
    print("=" * 60)

    review_date = input("\nReview Date (YYYY-MM-DD): ").strip()
    review_type = input("Review Type (Annual/Semi-annual/Quarterly): ").strip()
    period_start = input("Period Start (YYYY-MM-DD): ").strip()
    period_end = input("Period End (YYYY-MM-DD): ").strip()

    print("\nEnter Quality Metrics:")
    metrics = ReviewMetrics(
        complaint_rate=float(input("Complaint Rate (%): ") or 0),
        complaint_count=int(input("Complaint Count: ") or 0),
        capa_open=int(input("Open CAPAs: ") or 0),
        capa_overdue=int(input("Overdue CAPAs: ") or 0),
        capa_effectiveness=float(input("CAPA Effectiveness (%): ") or 0),
        audit_findings_open=int(input("Open Audit Findings: ") or 0),
        audit_findings_major=int(input("Major Audit Findings: ") or 0),
        first_pass_yield=float(input("First Pass Yield (%): ") or 0),
        customer_satisfaction=float(input("Customer Satisfaction (1-5): ") or 0),
        training_compliance=float(input("Training Compliance (%): ") or 0)
    )

    # Create review with sample inputs
    inputs = [
        ReviewInput(topic=topic, responsible=resp, status=InputStatus.COMPLETE, data_period=f"{period_start} to {period_end}")
        for topic, resp in ManagementReviewTracker.REQUIRED_INPUTS
    ]

    review = ManagementReview(
        review_date=review_date,
        review_type=review_type,
        period_start=period_start,
        period_end=period_end,
        inputs=inputs,
        actions=[],
        metrics=metrics
    )

    tracker = ManagementReviewTracker(review)
    report = tracker.generate_report()
    print("\n" + format_text_report(report))

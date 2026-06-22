# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402
from management_review_tracker_p0 import ActionItem, ActionPriority, ActionStatus, InputStatus, ManagementReview, ReviewInput, ReviewMetrics  # noqa: F401,E501
from management_review_tracker_p1 import format_text_report  # noqa: F401,E501
from management_review_tracker_p2 import interactive_mode  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description="Management Review Tracker"
    )
    parser.add_argument(
        "--data",
        type=str,
        help="JSON file with review data"
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
        help="Generate sample review data"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.sample:
        sample = {
            "review_date": "2024-06-30",
            "review_type": "Semi-annual",
            "period_start": "2024-01-01",
            "period_end": "2024-06-30",
            "inputs": [
                {"topic": "Audit Results", "responsible": "QA Manager", "status": "Complete", "data_period": "H1 2024"},
                {"topic": "Customer Feedback", "responsible": "Customer Quality", "status": "Complete", "data_period": "H1 2024"},
                {"topic": "Process Performance", "responsible": "Operations", "status": "In Progress", "data_period": "H1 2024"},
                {"topic": "CAPA Status", "responsible": "CAPA Officer", "status": "Complete", "data_period": "Current"}
            ],
            "actions": [
                {
                    "action_id": "MR-2024-001",
                    "description": "Implement enhanced CAPA tracking system",
                    "owner": "QA Manager",
                    "due_date": "2024-09-30",
                    "priority": "High",
                    "status": "In Progress",
                    "source_review": "2024-Q1"
                }
            ],
            "metrics": {
                "complaint_rate": 0.08,
                "complaint_count": 12,
                "capa_open": 8,
                "capa_overdue": 2,
                "capa_effectiveness": 88.0,
                "audit_findings_open": 5,
                "audit_findings_major": 1,
                "first_pass_yield": 96.5,
                "customer_satisfaction": 4.2,
                "training_compliance": 97.0
            }
        }
        print(json.dumps(sample, indent=2))
        return

    # Create sample review if no data provided
    if args.data:
        with open(args.data, "r") as f:
            data = json.load(f)

        inputs = [
            ReviewInput(
                topic=inp["topic"],
                responsible=inp["responsible"],
                status=InputStatus[inp["status"].upper().replace(" ", "_")],
                data_period=inp.get("data_period", "")
            )
            for inp in data.get("inputs", [])
        ]

        actions = [
            ActionItem(
                action_id=act["action_id"],
                description=act["description"],
                owner=act["owner"],
                due_date=act["due_date"],
                priority=ActionPriority[act["priority"].upper()],
                status=ActionStatus[act["status"].upper().replace(" ", "_")],
                source_review=act.get("source_review", "")
            )
            for act in data.get("actions", [])
        ]

        metrics_data = data.get("metrics", {})
        metrics = ReviewMetrics(**metrics_data)

        review = ManagementReview(
            review_date=data["review_date"],
            review_type=data["review_type"],
            period_start=data["period_start"],
            period_end=data["period_end"],
            inputs=inputs,
            actions=actions,
            metrics=metrics
        )
    else:
        # Demo data
        review = ManagementReview(
            review_date="2024-06-30",
            review_type="Semi-annual",
            period_start="2024-01-01",
            period_end="2024-06-30",
            inputs=[
                ReviewInput("Audit Results", "QA Manager", InputStatus.COMPLETE, "H1 2024"),
                ReviewInput("Customer Feedback", "Customer Quality", InputStatus.COMPLETE, "H1 2024"),
                ReviewInput("CAPA Status", "CAPA Officer", InputStatus.COMPLETE, "Current"),
            ],
            actions=[
                ActionItem("MR-2024-001", "Implement CAPA tracking", "QA Mgr", "2024-09-30",
                          ActionPriority.HIGH, ActionStatus.IN_PROGRESS, "2024-Q1"),
            ],
            metrics=ReviewMetrics(
                complaint_rate=0.08, capa_open=8, capa_overdue=2,
                capa_effectiveness=88.0, first_pass_yield=96.5,
                customer_satisfaction=4.2, training_compliance=97.0
            )
        )

    tracker = ManagementReviewTracker(review)
    report = tracker.generate_report()

    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text_report(report))

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402
from management_review_tracker_p0 import ActionStatus, InputStatus, ManagementReview  # noqa: F401,E501


class ManagementReviewTrackerMixin0:
    """Tracks and reports management review status."""
    REQUIRED_INPUTS = [
        ("Audit Results", "QA Manager"),
        ("Customer Feedback", "Customer Quality"),
        ("Process Performance", "Operations"),
        ("Product Conformity", "QC Manager"),
        ("CAPA Status", "CAPA Officer"),
        ("Previous Actions", "QMR"),
        ("QMS Changes", "RA Manager"),
        ("Recommendations", "All Managers"),
    ]
    def __init__(self, review: ManagementReview):
        self.review = review
        self.today = datetime.now()
    def check_input_readiness(self) -> Dict:
        """Check readiness of all required inputs."""
        readiness = {
            "total_required": len(self.REQUIRED_INPUTS),
            "complete": 0,
            "in_progress": 0,
            "not_started": 0,
            "missing_topics": [],
            "readiness_score": 0.0
        }

        input_topics = {inp.topic: inp for inp in self.review.inputs}

        for topic, responsible in self.REQUIRED_INPUTS:
            if topic in input_topics:
                inp = input_topics[topic]
                if inp.status in [InputStatus.COMPLETE, InputStatus.REVIEWED]:
                    readiness["complete"] += 1
                elif inp.status == InputStatus.IN_PROGRESS:
                    readiness["in_progress"] += 1
                else:
                    readiness["not_started"] += 1
            else:
                readiness["missing_topics"].append(topic)
                readiness["not_started"] += 1

        readiness["readiness_score"] = round(
            (readiness["complete"] / readiness["total_required"]) * 100, 1
        )

        return readiness
    def analyze_actions(self) -> Dict:
        """Analyze action item status."""
        analysis = {
            "total": len(self.review.actions),
            "by_status": {},
            "by_priority": {},
            "overdue": [],
            "due_soon": [],
            "completion_rate": 0.0
        }

        completed = 0
        for action in self.review.actions:
            # Count by status
            status = action.status.value
            analysis["by_status"][status] = analysis["by_status"].get(status, 0) + 1

            # Count by priority
            priority = action.priority.value
            analysis["by_priority"][priority] = analysis["by_priority"].get(priority, 0) + 1

            # Check completion
            if action.status in [ActionStatus.COMPLETE, ActionStatus.VERIFIED]:
                completed += 1

            # Check overdue
            if action.due_date:
                due = datetime.strptime(action.due_date, "%Y-%m-%d")
                if due < self.today and action.status not in [
                    ActionStatus.COMPLETE, ActionStatus.VERIFIED
                ]:
                    days_overdue = (self.today - due).days
                    analysis["overdue"].append({
                        "action_id": action.action_id,
                        "description": action.description[:50],
                        "owner": action.owner,
                        "days_overdue": days_overdue
                    })
                elif due <= self.today + timedelta(days=14) and action.status not in [
                    ActionStatus.COMPLETE, ActionStatus.VERIFIED
                ]:
                    days_until = (due - self.today).days
                    analysis["due_soon"].append({
                        "action_id": action.action_id,
                        "description": action.description[:50],
                        "owner": action.owner,
                        "days_until_due": days_until
                    })

        if analysis["total"] > 0:
            analysis["completion_rate"] = round((completed / analysis["total"]) * 100, 1)

        return analysis

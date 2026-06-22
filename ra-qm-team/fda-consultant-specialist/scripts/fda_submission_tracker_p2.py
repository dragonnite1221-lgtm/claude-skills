# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fda_submission_tracker_base import *  # noqa: F403,E402
# fmt: off
from fda_submission_tracker_p1 import FDA_TIMELINES, MILESTONES  # noqa: E402,E501
# fmt: on


def calculate_timeline_status(submission_type: str, milestones: Dict[str, str]) -> Dict:
    """Calculate timeline status based on submission type and milestone dates."""
    timeline_config = FDA_TIMELINES.get(submission_type, FDA_TIMELINES["510k_traditional"])

    result = {
        "submission_type": submission_type,
        "timeline_config": timeline_config,
        "status": "not_started",
        "days_elapsed": 0,
        "days_remaining": None,
        "projected_decision_date": None,
        "on_track": None
    }

    # Check if submission has been sent
    if "submission_sent" in milestones:
        try:
            submission_date = datetime.strptime(milestones["submission_sent"], "%Y-%m-%d")
            today = datetime.now()
            result["days_elapsed"] = (today - submission_date).days

            # Check for AI hold
            ai_hold_days = 0
            if "ai_request" in milestones and "ai_response" in milestones:
                ai_request_date = datetime.strptime(milestones["ai_request"], "%Y-%m-%d")
                ai_response_date = datetime.strptime(milestones["ai_response"], "%Y-%m-%d")
                ai_hold_days = (ai_response_date - ai_request_date).days
            elif "ai_request" in milestones and "ai_response" not in milestones:
                ai_request_date = datetime.strptime(milestones["ai_request"], "%Y-%m-%d")
                ai_hold_days = (today - ai_request_date).days
                result["status"] = "ai_hold"

            # Calculate review days (excluding AI hold)
            review_days = result["days_elapsed"] - ai_hold_days

            # Determine status
            if "se_decision" in milestones or "approval_decision" in milestones or "classification_decision" in milestones:
                result["status"] = "complete"
            elif "acceptance_decision" in milestones:
                result["status"] = "substantive_review"
            elif "acknowledgment_received" in milestones:
                result["status"] = "acceptance_review"
            else:
                result["status"] = "submitted"

            # Calculate projected decision date
            if result["status"] not in ["complete", "ai_hold"]:
                goal_days = timeline_config["total_goal"]
                result["days_remaining"] = max(0, goal_days - review_days)
                result["projected_decision_date"] = (submission_date + timedelta(days=goal_days + ai_hold_days)).strftime("%Y-%m-%d")
                result["on_track"] = review_days <= goal_days

        except ValueError:
            pass

    return result
def analyze_milestone_status(submission_type: str, completed_milestones: Dict[str, str]) -> List[Dict]:
    """Analyze milestone completion status."""
    milestone_list = MILESTONES.get(submission_type.split("_")[0], MILESTONES["510k"])

    results = []
    for milestone in milestone_list:
        status = {
            "id": milestone["id"],
            "name": milestone["name"],
            "phase": milestone["phase"],
            "optional": milestone.get("optional", False),
            "completed": milestone["id"] in completed_milestones,
            "completion_date": completed_milestones.get(milestone["id"])
        }
        results.append(status)

    return results

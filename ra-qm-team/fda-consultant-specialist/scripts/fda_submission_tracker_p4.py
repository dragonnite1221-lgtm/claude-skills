# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fda_submission_tracker_base import *  # noqa: F403,E402
# fmt: off
from fda_submission_tracker_p1 import find_submission_config  # noqa: E402,E501
from fda_submission_tracker_p2 import analyze_milestone_status, calculate_timeline_status  # noqa: E402,E501
from fda_submission_tracker_p3 import calculate_submission_readiness  # noqa: E402,E501
# fmt: on


def print_text_report(result: Dict) -> None:
    """Print human-readable report."""
    print("=" * 60)
    print("FDA SUBMISSION TRACKER REPORT")
    print("=" * 60)

    if "error" in result:
        print(f"\nError: {result['error']}")
        print(f"\nTo create a configuration file, run with --init")
        return

    # Basic info
    print(f"\nDevice: {result.get('device_name', 'Unknown')}")
    print(f"Submission Type: {result['submission_type']}")
    print(f"Product Code: {result.get('product_code', 'N/A')}")

    # Timeline status
    timeline = result["timeline_status"]
    print(f"\n--- Timeline Status ---")
    print(f"Status: {timeline['status'].upper()}")
    print(f"Days Elapsed: {timeline['days_elapsed']}")
    if timeline["days_remaining"] is not None:
        print(f"Days Remaining (FDA goal): {timeline['days_remaining']}")
    if timeline["projected_decision_date"]:
        print(f"Projected Decision Date: {timeline['projected_decision_date']}")
    if timeline["on_track"] is not None:
        status = "ON TRACK" if timeline["on_track"] else "BEHIND SCHEDULE"
        print(f"Timeline Status: {status}")

    # Milestones
    print(f"\n--- Milestones ---")
    for ms in result["milestones"]:
        status = "[X]" if ms["completed"] else "[ ]"
        optional = " (optional)" if ms["optional"] else ""
        date = f" - {ms['completion_date']}" if ms["completion_date"] else ""
        print(f"  {status} {ms['name']}{optional}{date}")

    # Readiness
    if "readiness" in result:
        print(f"\n--- Submission Readiness ---")
        readiness = result["readiness"]
        print(f"Readiness: {readiness['readiness_percentage']}% ({readiness['required_complete']}/{readiness['required_total']} required docs)")

        print("\n  Documents:")
        for doc in readiness["documents"]:
            status = "[X]" if doc["found"] else "[ ]"
            req = "(required)" if doc["required"] else "(optional)"
            path = f" - {doc['path']}" if doc["path"] else ""
            print(f"    {status} {doc['name']} {req}{path}")

    # Recommendations
    if result.get("recommendations"):
        print(f"\n--- Recommendations ---")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")

    print("\n" + "=" * 60)
def generate_recommendations(result: Dict) -> List[str]:
    """Generate actionable recommendations based on status."""
    recommendations = []

    timeline = result["timeline_status"]

    # Timeline recommendations
    if timeline["status"] == "ai_hold":
        recommendations.append("Priority: Respond to FDA Additional Information request within 180 days")
    elif timeline["on_track"] is False:
        recommendations.append("Warning: Submission is behind FDA review schedule - consider contacting FDA")

    # Milestone recommendations
    completed_phases = set()
    for ms in result["milestones"]:
        if ms["completed"]:
            completed_phases.add(ms["phase"])

    if "submission" not in completed_phases and "preparation" in completed_phases:
        recommendations.append("Ready for submission: Documentation complete, proceed with FDA submission")

    # Readiness recommendations
    if "readiness" in result:
        missing_required = [d for d in result["readiness"]["documents"] if d["required"] and not d["found"]]
        if missing_required:
            docs = ", ".join(d["name"] for d in missing_required[:3])
            recommendations.append(f"Missing required documentation: {docs}")

    return recommendations
def analyze_submission(project_dir: Path, submission_type: Optional[str] = None) -> Dict:
    """Main analysis function."""

    # Try to find existing configuration
    config = find_submission_config(project_dir)

    if config is None:
        # No config found - do basic analysis
        sub_type = submission_type or "510k_traditional"
        result = {
            "submission_type": sub_type,
            "config_found": False,
            "timeline_status": calculate_timeline_status(sub_type, {}),
            "milestones": analyze_milestone_status(sub_type, {}),
            "readiness": calculate_submission_readiness(project_dir, sub_type)
        }
    else:
        # Config found - full analysis
        sub_type = config.get("submission_type", submission_type or "510k_traditional")
        milestones = config.get("milestones", {})

        result = {
            "submission_type": sub_type,
            "device_name": config.get("device_name"),
            "product_code": config.get("product_code"),
            "predicate_device": config.get("predicate_device"),
            "config_found": True,
            "timeline_status": calculate_timeline_status(sub_type, milestones),
            "milestones": analyze_milestone_status(sub_type, milestones),
            "readiness": calculate_submission_readiness(project_dir, sub_type)
        }

    # Generate recommendations
    result["recommendations"] = generate_recommendations(result)

    return result

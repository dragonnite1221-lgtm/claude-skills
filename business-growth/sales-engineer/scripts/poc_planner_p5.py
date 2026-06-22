# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402
# fmt: off
from poc_planner_p1 import DEFAULT_PHASES  # noqa: E402,E501
from poc_planner_p2 import estimate_resources  # noqa: E402,E501
from poc_planner_p3 import generate_evaluation_scorecard, generate_success_criteria  # noqa: E402,E501
from poc_planner_p4 import identify_risks  # noqa: E402,E501
# fmt: on


def generate_go_no_go_framework(data: dict[str, Any]) -> dict[str, Any]:
    """Generate the go/no-go decision framework.

    Args:
        data: POC data.

    Returns:
        Go/no-go framework with criteria and thresholds.
    """
    return {
        "decision_criteria": [
            {
                "criterion": "Overall scorecard score",
                "go_threshold": ">=3.5 weighted average",
                "no_go_threshold": "<3.0 weighted average",
                "conditional_range": "3.0 - 3.5",
            },
            {
                "criterion": "Must-have success criteria met",
                "go_threshold": "100% of must-have criteria pass",
                "no_go_threshold": "<80% of must-have criteria pass",
                "conditional_range": "80-99% with mitigation plan",
            },
            {
                "criterion": "Stakeholder satisfaction",
                "go_threshold": "Champion and decision-maker both positive",
                "no_go_threshold": "Decision-maker negative",
                "conditional_range": "Mixed signals - needs follow-up",
            },
            {
                "criterion": "Technical blockers",
                "go_threshold": "No unresolved critical blockers",
                "no_go_threshold": ">2 unresolved critical blockers",
                "conditional_range": "1-2 blockers with clear resolution path",
            },
        ],
        "recommendation_logic": {
            "GO": "All criteria meet go thresholds, or majority go with no no-go triggers",
            "CONDITIONAL_GO": "Some criteria in conditional range, but no no-go triggers and clear resolution plan",
            "NO_GO": "Any criterion triggers no-go threshold without clear mitigation",
        },
    }
def plan_poc(data: dict[str, Any]) -> dict[str, Any]:
    """Run the complete POC planning pipeline.

    Args:
        data: Parsed POC data dictionary.

    Returns:
        Complete POC plan dictionary.
    """
    poc_info = {
        "poc_name": data.get("poc_name", "Unnamed POC"),
        "customer": data.get("customer", "Unknown Customer"),
        "opportunity_value": data.get("opportunity_value", "Not specified"),
        "complexity": data.get("complexity", "medium"),
        "start_date": data.get("start_date", "TBD"),
        "champion": data.get("champion", "Not identified"),
        "decision_maker": data.get("decision_maker", "Not identified"),
    }

    # Use custom phases if provided, otherwise defaults
    phases = data.get("phases", DEFAULT_PHASES)

    # Resource estimation
    resources = estimate_resources(data, phases)

    # Success criteria
    success_criteria = generate_success_criteria(data)

    # Evaluation scorecard
    scorecard = generate_evaluation_scorecard(data)

    # Risk identification
    risks = identify_risks(data, resources)

    # Go/No-Go framework
    go_no_go = generate_go_no_go_framework(data)

    # Timeline with phase details
    timeline = []
    current_week = 1
    for phase in phases:
        end_week = current_week + phase["duration_weeks"] - 1
        timeline.append({
            "phase": phase["name"],
            "start_week": current_week,
            "end_week": end_week,
            "duration_weeks": phase["duration_weeks"],
            "description": phase["description"],
            "activities": phase["activities"],
        })
        current_week = end_week + 1

    # Stakeholder plan
    stakeholders = data.get("stakeholders", [])
    stakeholder_plan = []
    for s in stakeholders:
        if isinstance(s, str):
            stakeholder_plan.append({
                "name": s,
                "role": "Evaluator",
                "engagement": "Weekly updates, phase reviews",
            })
        elif isinstance(s, dict):
            stakeholder_plan.append({
                "name": s.get("name", "Unknown"),
                "role": s.get("role", "Evaluator"),
                "engagement": s.get("engagement", "Weekly updates, phase reviews"),
            })

    return {
        "poc_info": poc_info,
        "timeline": timeline,
        "resource_allocation": resources,
        "success_criteria": success_criteria,
        "evaluation_scorecard": scorecard,
        "risk_register": risks,
        "go_no_go_framework": go_no_go,
        "stakeholder_plan": stakeholder_plan,
    }

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402


def identify_risks(data: dict[str, Any], resources: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify POC risks and generate mitigation strategies.

    Args:
        data: POC data.
        resources: Resource allocation data.

    Returns:
        List of risk entries with probability, impact, and mitigation.
    """
    risks = []
    complexity = data.get("complexity", "medium").lower()
    num_integrations = data.get("num_integrations", 0)
    total_weeks = resources["total_duration_weeks"]
    stakeholders = data.get("stakeholders", [])

    # Timeline risk
    if total_weeks > 6:
        risks.append({
            "risk": "Extended timeline may lose stakeholder attention",
            "probability": "high",
            "impact": "high",
            "mitigation": "Schedule weekly progress checkpoints; deliver early wins in week 2",
            "category": "Timeline",
        })
    elif total_weeks >= 4:
        risks.append({
            "risk": "Timeline may slip due to unforeseen technical issues",
            "probability": "medium",
            "impact": "medium",
            "mitigation": "Build 20% buffer into each phase; identify critical path early",
            "category": "Timeline",
        })

    # Integration risks
    if num_integrations > 3:
        risks.append({
            "risk": "Multiple integrations increase complexity and failure points",
            "probability": "high",
            "impact": "high",
            "mitigation": "Prioritize integrations by business value; test incrementally; have fallback demo data",
            "category": "Technical",
        })
    elif num_integrations > 0:
        risks.append({
            "risk": "Integration dependencies may cause delays",
            "probability": "medium",
            "impact": "medium",
            "mitigation": "Engage customer IT early; confirm API access and credentials in setup phase",
            "category": "Technical",
        })

    # Data risks
    risks.append({
        "risk": "Customer data quality or availability issues",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Request sample data early; prepare synthetic data as fallback; validate data format in setup",
        "category": "Data",
    })

    # Stakeholder risks
    if len(stakeholders) > 5:
        risks.append({
            "risk": "Too many stakeholders may slow decision-making",
            "probability": "medium",
            "impact": "medium",
            "mitigation": "Identify decision-maker and champion; schedule focused reviews per stakeholder group",
            "category": "Stakeholder",
        })

    if not stakeholders:
        risks.append({
            "risk": "Undefined stakeholder map may lead to misaligned evaluation",
            "probability": "high",
            "impact": "high",
            "mitigation": "Confirm stakeholder list, roles, and evaluation criteria before setup phase",
            "category": "Stakeholder",
        })

    # Resource risks
    if complexity == "high":
        risks.append({
            "risk": "High complexity may require additional engineering resources",
            "probability": "medium",
            "impact": "high",
            "mitigation": "Secure engineering commitment upfront; identify escalation path for blockers",
            "category": "Resource",
        })

    # Competitive risk
    risks.append({
        "risk": "Competitor POC running in parallel may shift evaluation criteria",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Stay close to champion; align success criteria early; differentiate on unique strengths",
        "category": "Competitive",
    })

    return risks

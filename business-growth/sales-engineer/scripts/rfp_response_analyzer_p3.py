# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402


def generate_risk_assessment(
    analyzed_reqs: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Generate risk assessment based on gaps and coverage patterns.

    Args:
        analyzed_reqs: List of analyzed requirement dictionaries.
        gaps: List of gap analysis entries.

    Returns:
        List of risk entries with impact and mitigation.
    """
    risks = []

    critical_gaps = [g for g in gaps if g["severity"] == "critical"]
    if critical_gaps:
        risks.append({
            "risk": "Critical requirement gaps",
            "impact": "high",
            "description": f"{len(critical_gaps)} must-have requirements not fully met",
            "mitigation": "Prioritize engineering effort or partner integration for gap closure",
        })

    total_effort = sum(r["effort_hours"] for r in analyzed_reqs if r["coverage_status"] != "full")
    if total_effort > 200:
        risks.append({
            "risk": "High customization effort",
            "impact": "high",
            "description": f"{total_effort} hours estimated for non-full requirements",
            "mitigation": "Evaluate resource availability and timeline feasibility before committing",
        })
    elif total_effort > 80:
        risks.append({
            "risk": "Moderate customization effort",
            "impact": "medium",
            "description": f"{total_effort} hours estimated for non-full requirements",
            "mitigation": "Phase implementation and set clear expectations on delivery timeline",
        })

    planned_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "planned")
    if planned_count > 3:
        risks.append({
            "risk": "Roadmap dependency",
            "impact": "medium",
            "description": f"{planned_count} requirements depend on planned product features",
            "mitigation": "Confirm roadmap timelines with product team; include contractual commitments if needed",
        })

    partial_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "partial")
    if partial_count > 5:
        risks.append({
            "risk": "Workaround complexity",
            "impact": "medium",
            "description": f"{partial_count} requirements need workarounds or configuration",
            "mitigation": "Document workarounds clearly; plan for native support in future releases",
        })

    if not risks:
        risks.append({
            "risk": "No significant risks identified",
            "impact": "low",
            "description": "Strong coverage across all requirement categories",
            "mitigation": "Maintain standard engagement process",
        })

    return risks

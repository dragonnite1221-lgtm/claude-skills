# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402
# fmt: off
from rfp_response_analyzer_p1 import analyze_requirement, generate_gap_analysis, safe_divide  # noqa: E402,E501
from rfp_response_analyzer_p2 import compute_category_scores, determine_bid_recommendation  # noqa: E402,E501
from rfp_response_analyzer_p3 import generate_risk_assessment  # noqa: E402,E501
# fmt: on


def analyze_rfp(data: dict[str, Any]) -> dict[str, Any]:
    """Run the complete RFP analysis pipeline.

    Args:
        data: Parsed RFP data with requirements array.

    Returns:
        Complete analysis results dictionary.
    """
    rfp_info = {
        "rfp_name": data.get("rfp_name", "Unnamed RFP"),
        "customer": data.get("customer", "Unknown Customer"),
        "due_date": data.get("due_date", "Not specified"),
        "strategic_value": data.get("strategic_value", "medium"),
        "deal_value": data.get("deal_value", "Not specified"),
    }

    # Analyze each requirement
    analyzed_reqs = [analyze_requirement(req) for req in data["requirements"]]

    # Compute overall scores
    total_weighted = sum(r["weighted_score"] for r in analyzed_reqs)
    total_max = sum(r["max_weighted"] for r in analyzed_reqs)
    overall_coverage = safe_divide(total_weighted, total_max) * 100

    # Coverage summary
    total_count = len(analyzed_reqs)
    full_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "full")
    partial_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "partial")
    planned_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "planned")
    gap_count = sum(1 for r in analyzed_reqs if r["coverage_status"] == "gap")

    # Must-have gap count
    must_have_gaps = sum(
        1 for r in analyzed_reqs
        if r["priority"] == "must-have" and r["coverage_status"] == "gap"
    )

    # Category breakdown
    category_scores = compute_category_scores(analyzed_reqs)

    # Gap analysis
    gaps = generate_gap_analysis(analyzed_reqs)

    # Bid recommendation
    bid_recommendation = determine_bid_recommendation(
        overall_coverage,
        must_have_gaps,
        rfp_info["strategic_value"],
    )

    # Risk assessment
    risks = generate_risk_assessment(analyzed_reqs, gaps)

    # Effort summary
    total_effort = sum(r["effort_hours"] for r in analyzed_reqs)
    gap_effort = sum(r["effort_hours"] for r in analyzed_reqs if r["coverage_status"] != "full")

    return {
        "rfp_info": rfp_info,
        "coverage_summary": {
            "overall_coverage_percentage": round(overall_coverage, 1),
            "total_requirements": total_count,
            "full": full_count,
            "partial": partial_count,
            "planned": planned_count,
            "gap": gap_count,
            "must_have_gaps": must_have_gaps,
        },
        "category_scores": category_scores,
        "bid_recommendation": bid_recommendation,
        "gap_analysis": gaps,
        "risk_assessment": risks,
        "effort_estimate": {
            "total_hours": total_effort,
            "gap_closure_hours": gap_effort,
            "full_coverage_hours": total_effort - gap_effort,
        },
        "requirements_detail": analyzed_reqs,
    }

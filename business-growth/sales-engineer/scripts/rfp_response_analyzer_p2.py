# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402
# fmt: off
from rfp_response_analyzer_p1 import BID_THRESHOLD, CONDITIONAL_THRESHOLD, MAX_MUST_HAVE_GAPS_FOR_BID, safe_divide  # noqa: E402,E501
# fmt: on


def compute_category_scores(analyzed_reqs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Compute coverage scores grouped by requirement category.

    Args:
        analyzed_reqs: List of analyzed requirement dictionaries.

    Returns:
        Dictionary of category names to score summaries.
    """
    categories: dict[str, dict[str, float]] = {}

    for req in analyzed_reqs:
        cat = req["category"]
        if cat not in categories:
            categories[cat] = {
                "weighted_score": 0.0,
                "max_weighted": 0.0,
                "count": 0,
                "full_count": 0,
                "partial_count": 0,
                "planned_count": 0,
                "gap_count": 0,
                "effort_hours": 0,
            }

        categories[cat]["weighted_score"] += req["weighted_score"]
        categories[cat]["max_weighted"] += req["max_weighted"]
        categories[cat]["count"] += 1
        categories[cat]["effort_hours"] += req["effort_hours"]

        status_key = f"{req['coverage_status']}_count"
        if status_key in categories[cat]:
            categories[cat][status_key] += 1

    result = {}
    for cat, scores in categories.items():
        coverage_pct = safe_divide(scores["weighted_score"], scores["max_weighted"]) * 100
        result[cat] = {
            "coverage_percentage": round(coverage_pct, 1),
            "requirements_count": int(scores["count"]),
            "full": int(scores["full_count"]),
            "partial": int(scores["partial_count"]),
            "planned": int(scores["planned_count"]),
            "gap": int(scores["gap_count"]),
            "effort_hours": int(scores["effort_hours"]),
        }

    return result
def determine_bid_recommendation(
    overall_coverage: float,
    must_have_gaps: int,
    strategic_value: str,
) -> dict[str, Any]:
    """Determine bid/no-bid recommendation based on coverage and gaps.

    Args:
        overall_coverage: Overall weighted coverage percentage (0-100).
        must_have_gaps: Number of must-have requirements with gap status.
        strategic_value: Strategic value assessment (high, medium, low).

    Returns:
        Recommendation dictionary with decision and rationale.
    """
    coverage_ratio = overall_coverage / 100.0
    reasons = []

    # Primary decision logic
    if coverage_ratio >= BID_THRESHOLD and must_have_gaps <= MAX_MUST_HAVE_GAPS_FOR_BID:
        decision = "BID"
        reasons.append(f"Coverage score {overall_coverage:.1f}% exceeds {BID_THRESHOLD*100:.0f}% threshold")
        if must_have_gaps > 0:
            reasons.append(f"{must_have_gaps} must-have gap(s) within acceptable range (max {MAX_MUST_HAVE_GAPS_FOR_BID})")
    elif coverage_ratio >= CONDITIONAL_THRESHOLD or (
        must_have_gaps <= MAX_MUST_HAVE_GAPS_FOR_BID and coverage_ratio >= 0.4
    ):
        decision = "CONDITIONAL BID"
        reasons.append(f"Coverage score {overall_coverage:.1f}% in conditional range ({CONDITIONAL_THRESHOLD*100:.0f}%-{BID_THRESHOLD*100:.0f}%)")
        if must_have_gaps > 0:
            reasons.append(f"{must_have_gaps} must-have gap(s) require mitigation plan")
    else:
        decision = "NO-BID"
        if coverage_ratio < CONDITIONAL_THRESHOLD:
            reasons.append(f"Coverage score {overall_coverage:.1f}% below {CONDITIONAL_THRESHOLD*100:.0f}% minimum")
        if must_have_gaps > MAX_MUST_HAVE_GAPS_FOR_BID:
            reasons.append(f"{must_have_gaps} must-have gaps exceed maximum of {MAX_MUST_HAVE_GAPS_FOR_BID}")

    # Strategic value adjustment
    if strategic_value.lower() == "high" and decision == "CONDITIONAL BID":
        reasons.append("High strategic value supports pursuing despite coverage gaps")
    elif strategic_value.lower() == "low" and decision == "CONDITIONAL BID":
        decision = "NO-BID"
        reasons.append("Low strategic value does not justify investment for conditional coverage")

    confidence = "high" if coverage_ratio >= 0.80 else (
        "medium" if coverage_ratio >= 0.60 else "low"
    )

    return {
        "decision": decision,
        "confidence": confidence,
        "overall_coverage_percentage": round(overall_coverage, 1),
        "must_have_gaps": must_have_gaps,
        "strategic_value": strategic_value,
        "reasons": reasons,
    }

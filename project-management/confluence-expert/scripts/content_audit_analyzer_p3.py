# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_audit_analyzer_base import *  # noqa: F403,E402
# fmt: off
from content_audit_analyzer_p1 import HEALTH_WEIGHTS, check_engagement, check_organization, check_stale_pages  # noqa: E402,E501
from content_audit_analyzer_p2 import _generate_action_items, check_completeness, check_size_balance  # noqa: E402,E501
# fmt: on


def analyze_content_health(data: Dict[str, Any]) -> Dict[str, Any]:
    """Run full content audit analysis."""
    pages = data.get("pages", [])

    if not pages:
        return {
            "health_score": 0,
            "grade": "invalid",
            "error": "No pages found in input data",
            "dimensions": {},
            "action_items": [],
        }

    reference_date = datetime.now()

    # Run all checks
    dimensions = {
        "freshness": check_stale_pages(pages, reference_date),
        "engagement": check_engagement(pages),
        "organization": check_organization(pages),
        "size_balance": check_size_balance(pages),
        "completeness": check_completeness(pages),
    }

    # Calculate weighted health score
    weighted_scores = []
    for dim_name, dim_result in dimensions.items():
        weight = HEALTH_WEIGHTS.get(dim_name, 0.1)
        weighted_scores.append(dim_result["score"] * weight)

    health_score = sum(weighted_scores)

    if health_score >= 85:
        grade = "excellent"
    elif health_score >= 70:
        grade = "good"
    elif health_score >= 55:
        grade = "fair"
    else:
        grade = "poor"

    # Generate action items
    action_items = _generate_action_items(dimensions)

    return {
        "health_score": round(health_score, 1),
        "grade": grade,
        "total_pages": len(pages),
        "dimensions": dimensions,
        "action_items": action_items,
    }
def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("CONTENT AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    if "error" in result:
        lines.append(f"ERROR: {result['error']}")
        return "\n".join(lines)

    lines.append("HEALTH SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Health Score: {result['health_score']}/100")
    lines.append(f"Grade: {result['grade'].title()}")
    lines.append(f"Total Pages Analyzed: {result['total_pages']}")
    lines.append("")

    # Dimension scores
    lines.append("DIMENSION SCORES")
    lines.append("-" * 30)
    for dim_name, dim_data in result.get("dimensions", {}).items():
        weight = HEALTH_WEIGHTS.get(dim_name, 0)
        lines.append(f"{dim_name.replace('_', ' ').title()} (Weight: {weight:.0%})")
        lines.append(f"  Score: {dim_data['score']:.1f}/100")

        if dim_name == "freshness":
            lines.append(f"  Stale: {dim_data.get('stale_count', 0)}, Outdated: {dim_data.get('outdated_count', 0)}, Fresh: {dim_data.get('fresh_count', 0)}")
        elif dim_name == "engagement":
            lines.append(f"  Low Engagement: {dim_data.get('low_engagement_count', 0)}, Avg Views: {dim_data.get('average_views', 0)}")
        elif dim_name == "organization":
            lines.append(f"  Orphaned (no labels): {dim_data.get('orphaned_count', 0)}, Labeled: {dim_data.get('labeled_count', 0)}")
        elif dim_name == "size_balance":
            lines.append(f"  Oversized: {dim_data.get('oversized_count', 0)}, Undersized: {dim_data.get('undersized_count', 0)}, Avg Words: {dim_data.get('average_word_count', 0)}")
        elif dim_name == "completeness":
            lines.append(f"  Incomplete: {dim_data.get('incomplete_count', 0)}, Complete: {dim_data.get('complete_count', 0)}")
        lines.append("")

    # Action items
    action_items = result.get("action_items", [])
    if action_items:
        lines.append("ACTION ITEMS")
        lines.append("-" * 30)
        for i, item in enumerate(action_items, 1):
            priority = item["priority"].upper()
            lines.append(f"{i}. [{priority}] {item['action']}")
        lines.append("")

    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result

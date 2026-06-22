# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_score_calculator_base import *  # noqa: F403,E402
# fmt: off
from health_score_calculator_p1 import DIMENSION_WEIGHTS, classify, get_benchmarks, safe_divide, score_usage, trend_direction  # noqa: E402,E501
from health_score_calculator_p2 import score_engagement, score_relationship, score_support  # noqa: E402,E501
# fmt: on


def calculate_health_score(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the overall health score for a single customer."""
    segment = customer.get("segment", "mid-market").lower()
    benchmarks = get_benchmarks(segment)

    # Score each dimension
    usage_score, usage_recs = score_usage(customer.get("usage", {}), benchmarks)
    engagement_score, engagement_recs = score_engagement(customer.get("engagement", {}), benchmarks)
    support_score, support_recs = score_support(customer.get("support", {}), benchmarks)
    relationship_score, relationship_recs = score_relationship(customer.get("relationship", {}), benchmarks)

    # Weighted overall
    overall = round(
        usage_score * DIMENSION_WEIGHTS["usage"]
        + engagement_score * DIMENSION_WEIGHTS["engagement"]
        + support_score * DIMENSION_WEIGHTS["support"]
        + relationship_score * DIMENSION_WEIGHTS["relationship"],
        1,
    )

    classification = classify(overall, segment)

    # Trend analysis
    prev = customer.get("previous_period", {})
    trends = {
        "usage": trend_direction(usage_score, prev.get("usage_score")),
        "engagement": trend_direction(engagement_score, prev.get("engagement_score")),
        "support": trend_direction(support_score, prev.get("support_score")),
        "relationship": trend_direction(relationship_score, prev.get("relationship_score")),
    }
    overall_prev = prev.get("overall_score")
    trends["overall"] = trend_direction(overall, overall_prev)

    # Combine recommendations
    all_recs = usage_recs + engagement_recs + support_recs + relationship_recs

    return {
        "customer_id": customer.get("customer_id", "unknown"),
        "name": customer.get("name", "Unknown"),
        "segment": segment,
        "arr": customer.get("arr", 0),
        "overall_score": overall,
        "classification": classification,
        "dimensions": {
            "usage": {"score": usage_score, "weight": "30%", "classification": classify(usage_score, segment)},
            "engagement": {"score": engagement_score, "weight": "25%", "classification": classify(engagement_score, segment)},
            "support": {"score": support_score, "weight": "20%", "classification": classify(support_score, segment)},
            "relationship": {"score": relationship_score, "weight": "25%", "classification": classify(relationship_score, segment)},
        },
        "trends": trends,
        "recommendations": all_recs,
    }
CLASSIFICATION_LABELS = {
    "green": "HEALTHY",
    "yellow": "NEEDS ATTENTION",
    "red": "AT RISK",
}
def format_text(results: List[Dict[str, Any]]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 72)
    lines.append("CUSTOMER HEALTH SCORE REPORT")
    lines.append("=" * 72)
    lines.append("")

    # Portfolio summary
    total = len(results)
    green_count = sum(1 for r in results if r["classification"] == "green")
    yellow_count = sum(1 for r in results if r["classification"] == "yellow")
    red_count = sum(1 for r in results if r["classification"] == "red")
    avg_score = round(safe_divide(sum(r["overall_score"] for r in results), total), 1)

    lines.append(f"Portfolio Summary: {total} customers")
    lines.append(f"  Average Health Score: {avg_score}/100")
    lines.append(f"  Green (Healthy):       {green_count}")
    lines.append(f"  Yellow (Attention):     {yellow_count}")
    lines.append(f"  Red (At Risk):         {red_count}")
    lines.append("")

    for r in results:
        label = CLASSIFICATION_LABELS.get(r["classification"], "UNKNOWN")
        lines.append("-" * 72)
        lines.append(f"Customer: {r['name']} ({r['customer_id']})")
        lines.append(f"Segment:  {r['segment'].title()}  |  ARR: ${r['arr']:,.0f}")
        lines.append(f"Overall Score: {r['overall_score']}/100  [{label}]")
        lines.append("")

        lines.append("  Dimension Scores:")
        for dim_name, dim_data in r["dimensions"].items():
            dim_label = CLASSIFICATION_LABELS.get(dim_data["classification"], "")
            lines.append(f"    {dim_name.title():15s} {dim_data['score']:6.1f}/100  ({dim_data['weight']})  [{dim_label}]")

        lines.append("")
        lines.append("  Trends:")
        for dim_name, direction in r["trends"].items():
            arrow = {"improving": "+", "declining": "-", "stable": "=", "no_data": "?"}
            lines.append(f"    {dim_name.title():15s} {arrow.get(direction, '?')} {direction}")

        if r["recommendations"]:
            lines.append("")
            lines.append("  Recommendations:")
            for i, rec in enumerate(r["recommendations"], 1):
                lines.append(f"    {i}. {rec}")

        lines.append("")

    lines.append("=" * 72)
    return "\n".join(lines)
def format_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON."""
    total = len(results)
    output = {
        "report": "customer_health_scores",
        "summary": {
            "total_customers": total,
            "average_score": round(safe_divide(sum(r["overall_score"] for r in results), total), 1),
            "green_count": sum(1 for r in results if r["classification"] == "green"),
            "yellow_count": sum(1 for r in results if r["classification"] == "yellow"),
            "red_count": sum(1 for r in results if r["classification"] == "red"),
        },
        "customers": results,
    }
    return json.dumps(output, indent=2)

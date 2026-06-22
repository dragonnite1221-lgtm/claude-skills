# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402


def format_text(result: dict[str, Any]) -> str:
    """Format analysis results as human-readable text.

    Args:
        result: Complete analysis results dictionary.

    Returns:
        Formatted text string.
    """
    lines = []
    info = result["rfp_info"]
    lines.append("=" * 70)
    lines.append("RFP RESPONSE ANALYSIS")
    lines.append("=" * 70)
    lines.append(f"RFP:            {info['rfp_name']}")
    lines.append(f"Customer:       {info['customer']}")
    lines.append(f"Due Date:       {info['due_date']}")
    lines.append(f"Deal Value:     {info['deal_value']}")
    lines.append(f"Strategic Value: {info['strategic_value'].upper()}")
    lines.append("")

    # Coverage summary
    cs = result["coverage_summary"]
    lines.append("-" * 70)
    lines.append("COVERAGE SUMMARY")
    lines.append("-" * 70)
    lines.append(f"Overall Coverage:  {cs['overall_coverage_percentage']}%")
    lines.append(f"Total Requirements: {cs['total_requirements']}")
    lines.append(f"  Full:    {cs['full']}  |  Partial: {cs['partial']}  |  Planned: {cs['planned']}  |  Gap: {cs['gap']}")
    lines.append(f"Must-Have Gaps:    {cs['must_have_gaps']}")
    lines.append("")

    # Bid recommendation
    bid = result["bid_recommendation"]
    lines.append("-" * 70)
    lines.append(f"BID RECOMMENDATION: {bid['decision']}")
    lines.append(f"Confidence: {bid['confidence'].upper()}")
    lines.append("-" * 70)
    for reason in bid["reasons"]:
        lines.append(f"  - {reason}")
    lines.append("")

    # Category scores
    lines.append("-" * 70)
    lines.append("CATEGORY BREAKDOWN")
    lines.append("-" * 70)
    lines.append(f"{'Category':<25} {'Coverage':>8} {'Full':>5} {'Part':>5} {'Plan':>5} {'Gap':>5} {'Effort':>7}")
    lines.append("-" * 70)
    for cat, scores in result["category_scores"].items():
        lines.append(
            f"{cat:<25} {scores['coverage_percentage']:>7.1f}% "
            f"{scores['full']:>5} {scores['partial']:>5} "
            f"{scores['planned']:>5} {scores['gap']:>5} "
            f"{scores['effort_hours']:>6}h"
        )
    lines.append("")

    # Gap analysis
    gaps = result["gap_analysis"]
    if gaps:
        lines.append("-" * 70)
        lines.append("GAP ANALYSIS")
        lines.append("-" * 70)
        for gap in gaps:
            severity_marker = "!!!" if gap["severity"] == "critical" else (
                "!!" if gap["severity"] == "high" else "!"
            )
            lines.append(f"  [{severity_marker}] {gap['id']}: {gap['requirement']}")
            lines.append(f"       Category: {gap['category']} | Priority: {gap['priority']} | Status: {gap['coverage_status']}")
            lines.append(f"       Effort: {gap['effort_hours']}h | Mitigation: {gap['mitigation']}")
            lines.append("")

    # Risk assessment
    risks = result["risk_assessment"]
    lines.append("-" * 70)
    lines.append("RISK ASSESSMENT")
    lines.append("-" * 70)
    for risk in risks:
        lines.append(f"  [{risk['impact'].upper()}] {risk['risk']}")
        lines.append(f"       {risk['description']}")
        lines.append(f"       Mitigation: {risk['mitigation']}")
        lines.append("")

    # Effort estimate
    effort = result["effort_estimate"]
    lines.append("-" * 70)
    lines.append("EFFORT ESTIMATE")
    lines.append("-" * 70)
    lines.append(f"  Total Effort:         {effort['total_hours']} hours")
    lines.append(f"  Gap Closure Effort:   {effort['gap_closure_hours']} hours")
    lines.append(f"  Supported Effort:     {effort['full_coverage_hours']} hours")
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)

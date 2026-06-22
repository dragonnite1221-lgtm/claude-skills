# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402


def format_text(result: dict[str, Any]) -> str:
    """Format POC plan as human-readable text.

    Args:
        result: Complete POC plan dictionary.

    Returns:
        Formatted text string.
    """
    lines = []
    info = result["poc_info"]

    lines.append("=" * 70)
    lines.append("PROOF OF CONCEPT PLAN")
    lines.append("=" * 70)
    lines.append(f"POC Name:          {info['poc_name']}")
    lines.append(f"Customer:          {info['customer']}")
    lines.append(f"Opportunity Value: {info['opportunity_value']}")
    lines.append(f"Complexity:        {info['complexity'].upper()}")
    lines.append(f"Start Date:        {info['start_date']}")
    lines.append(f"Champion:          {info['champion']}")
    lines.append(f"Decision Maker:    {info['decision_maker']}")
    lines.append("")

    # Timeline
    lines.append("-" * 70)
    lines.append("TIMELINE")
    lines.append("-" * 70)
    for phase in result["timeline"]:
        week_range = (
            f"Week {phase['start_week']}"
            if phase["start_week"] == phase["end_week"]
            else f"Weeks {phase['start_week']}-{phase['end_week']}"
        )
        lines.append(f"\n  Phase: {phase['phase']} ({week_range})")
        lines.append(f"  {phase['description']}")
        lines.append("  Activities:")
        for activity in phase["activities"]:
            lines.append(f"    - {activity}")
    lines.append("")

    # Resource allocation
    res = result["resource_allocation"]
    lines.append("-" * 70)
    lines.append("RESOURCE ALLOCATION")
    lines.append("-" * 70)
    lines.append(f"Total Duration:    {res['total_duration_weeks']} weeks")
    lines.append(f"Complexity:        {res['complexity'].upper()}")
    lines.append("")
    lines.append("  Totals:")
    lines.append(f"    SE Hours:           {res['totals']['se_hours']}")
    lines.append(f"    Engineering Hours:  {res['totals']['engineering_hours']}")
    lines.append(f"    Customer Hours:     {res['totals']['customer_hours']}")
    lines.append(f"    Total Hours:        {res['totals']['total_hours']}")
    lines.append("")
    lines.append("  Phase Breakdown:")
    lines.append(f"    {'Phase':<20} {'Weeks':>5} {'SE':>6} {'Eng':>6} {'Cust':>6}")
    lines.append("    " + "-" * 45)
    for pr in res["phase_breakdown"]:
        lines.append(
            f"    {pr['phase']:<20} {pr['duration_weeks']:>5} "
            f"{pr['se_hours']:>5}h {pr['engineering_hours']:>5}h {pr['customer_hours']:>5}h"
        )
    lines.append("")

    # Success criteria
    criteria = result["success_criteria"]
    lines.append("-" * 70)
    lines.append("SUCCESS CRITERIA")
    lines.append("-" * 70)
    for i, sc in enumerate(criteria, 1):
        priority_marker = "[MUST]" if sc["priority"] == "must-have" else (
            "[SHOULD]" if sc["priority"] == "should-have" else "[NICE]"
        )
        lines.append(f"  {i}. {priority_marker} {sc['criterion']}")
        lines.append(f"     Metric: {sc['metric']}")
        lines.append(f"     Target: {sc['target']}")
        lines.append(f"     Category: {sc['category']}")
        lines.append("")

    # Evaluation scorecard
    scorecard = result["evaluation_scorecard"]
    lines.append("-" * 70)
    lines.append("EVALUATION SCORECARD")
    lines.append("-" * 70)
    lines.append(f"  Pass Threshold:        {scorecard['pass_threshold']}/5.0")
    lines.append(f"  Strong Pass Threshold: {scorecard['strong_pass_threshold']}/5.0")
    lines.append("")
    lines.append("  Scoring Scale:")
    for score, desc in scorecard["scoring_scale"].items():
        lines.append(f"    {score} = {desc}")
    lines.append("")
    lines.append("  Categories:")
    for cat_name, cat_data in scorecard["categories"].items():
        lines.append(f"\n    {cat_name} (weight: {cat_data['weight']:.0%})")
        for criterion in cat_data["criteria"]:
            lines.append(f"      [ ] {criterion}")
    lines.append("")

    # Risk register
    risks = result["risk_register"]
    lines.append("-" * 70)
    lines.append("RISK REGISTER")
    lines.append("-" * 70)
    for risk in risks:
        lines.append(f"  [{risk['impact'].upper()}] {risk['risk']}")
        lines.append(f"       Probability: {risk['probability']} | Impact: {risk['impact']}")
        lines.append(f"       Category: {risk['category']}")
        lines.append(f"       Mitigation: {risk['mitigation']}")
        lines.append("")

    # Go/No-Go framework
    framework = result["go_no_go_framework"]
    lines.append("-" * 70)
    lines.append("GO / NO-GO DECISION FRAMEWORK")
    lines.append("-" * 70)
    for dc in framework["decision_criteria"]:
        lines.append(f"  {dc['criterion']}:")
        lines.append(f"    GO:          {dc['go_threshold']}")
        lines.append(f"    CONDITIONAL: {dc['conditional_range']}")
        lines.append(f"    NO-GO:       {dc['no_go_threshold']}")
        lines.append("")

    lines.append("  Recommendation Logic:")
    for decision, logic in framework["recommendation_logic"].items():
        lines.append(f"    {decision}: {logic}")
    lines.append("")

    # Stakeholder plan
    stakeholders = result["stakeholder_plan"]
    if stakeholders:
        lines.append("-" * 70)
        lines.append("STAKEHOLDER PLAN")
        lines.append("-" * 70)
        for s in stakeholders:
            lines.append(f"  {s['name']} ({s['role']})")
            lines.append(f"    Engagement: {s['engagement']}")
            lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)

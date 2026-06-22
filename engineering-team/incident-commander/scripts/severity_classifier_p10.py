# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import DIMENSION_WEIGHTS, SeverityLevel  # noqa: E402,E501
from severity_classifier_p2 import ActionPlan, EscalationPath, SLAImpact, SeverityScore  # noqa: E402,E501
# fmt: on


def format_markdown(
    incident: Dict,
    severity_score: SeverityScore,
    escalation: EscalationPath,
    action_plan: ActionPlan,
    sla_impact: SLAImpact,
) -> str:
    """Render a Markdown report suitable for incident tickets or wikis."""
    lines: List[str] = []
    sev_def = SeverityLevel.get_definition(severity_score.severity_level)

    lines.append(f"# Incident Severity Classification: {severity_score.severity_level}")
    lines.append("")
    lines.append(f"**Classified:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    lines.append("## Incident Summary")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Title | {incident.get('title', 'N/A')} |")
    lines.append(f"| Service | {incident.get('service', 'N/A')} |")
    lines.append(f"| Detected | {incident.get('detected_at', 'N/A')} |")
    lines.append(f"| Reporter | {incident.get('reporter', 'N/A')} |")
    lines.append("")

    lines.append("## Severity Classification")
    lines.append("")
    lines.append(
        f"> **{severity_score.severity_level} -- {sev_def['label']}** "
        f"(Score: {severity_score.composite_score:.3f})"
    )
    lines.append(f">")
    lines.append(f"> {sev_def['description']}")
    lines.append("")

    lines.append("### Dimension Scores")
    lines.append("")
    lines.append("| Dimension | Raw | Weight | Weighted |")
    lines.append("|-----------|-----|--------|----------|")
    for dim, raw in severity_score.dimensions.items():
        wt = severity_score.weighted_dimensions.get(dim, 0)
        weight_cfg = DIMENSION_WEIGHTS.get(dim, 0)
        label = dim.replace("_", " ").title()
        lines.append(f"| {label} | {raw:.3f} | {weight_cfg:.2f} | {wt:.3f} |")
    lines.append("")

    if severity_score.contributing_factors:
        lines.append("### Contributing Factors")
        lines.append("")
        for f in severity_score.contributing_factors:
            lines.append(f"- {f}")
        lines.append("")

    if severity_score.auto_escalate_reasons:
        lines.append("### Auto-Escalation Overrides")
        lines.append("")
        for r in severity_score.auto_escalate_reasons:
            lines.append(f"- **{r}**")
        lines.append("")

    lines.append("## Escalation Path")
    lines.append("")
    lines.append(f"**Immediate Notify:** {', '.join(escalation.immediate_notify)}")
    lines.append("")

    if escalation.war_room_required:
        lines.append(f"**War Room:** [Join Bridge]({escalation.bridge_link})")
    else:
        lines.append("**War Room:** Not required")
    lines.append("")

    if escalation.escalation_chain:
        lines.append("### Escalation Chain")
        lines.append("")
        for step in escalation.escalation_chain:
            lines.append(
                f"- **After {step['trigger_after_minutes']} min:** "
                f"Notify {', '.join(step['notify'])} -- {step['reason']}"
            )
        lines.append("")

    if escalation.cross_team_notify:
        lines.append(f"**Cross-Team:** {', '.join(escalation.cross_team_notify)}")
        lines.append("")

    if escalation.suggested_smes:
        lines.append("### Suggested SMEs")
        lines.append("")
        for sme in escalation.suggested_smes:
            lines.append(f"- {sme}")
        lines.append("")

    lines.append("## Action Plan")
    lines.append("")

    lines.append("### Immediate Actions")
    lines.append("")
    for i, action in enumerate(action_plan.immediate_actions, 1):
        lines.append(f"{i}. {action}")
    lines.append("")

    lines.append("### Diagnostic Steps")
    lines.append("")
    for i, step in enumerate(action_plan.diagnostic_steps, 1):
        lines.append(f"{i}. {step}")
    lines.append("")

    lines.append("### Communication")
    lines.append("")
    for i, action in enumerate(action_plan.communication_actions, 1):
        lines.append(f"{i}. {action}")
    lines.append("")

    rb = action_plan.rollback_assessment
    lines.append("### Rollback Assessment")
    lines.append("")
    if rb.get("recent_deployment_detected"):
        lines.append(
            f"| Deploy | {rb.get('service', '?')} v{rb.get('version', '?')} |"
        )
        lines.append(f"|--------|------|")
        lines.append(f"| Deployed At | {rb.get('deployed_at', '?')} |")
        if "minutes_since_deploy" in rb:
            lines.append(f"| Minutes Before Detection | {rb['minutes_since_deploy']} |")
        lines.append("")
    lines.append(f"**Recommendation:** {rb.get('recommendation', 'N/A')}")
    lines.append("")

    lines.append("## SLA Impact")
    lines.append("")
    tier = sla_impact.sla_tier
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Breach Risk | **{sla_impact.breach_risk.upper()}** |")
    lines.append(f"| Error Budget Impact | {sla_impact.error_budget_impact_minutes} min/hr |")
    lines.append(f"| Remaining Budget | {sla_impact.remaining_budget_percentage}% |")
    lines.append(f"| Est. Time to Breach | {sla_impact.estimated_time_to_breach_minutes} min |")
    lines.append(f"| Target Resolution | {tier.get('target_resolution_hours', '?')} hours |")
    lines.append(f"| Target Response | {tier.get('target_response_minutes', '?')} minutes |")
    lines.append("")

    if sla_impact.recommendations:
        lines.append("### SLA Recommendations")
        lines.append("")
        for rec in sla_impact.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by severity_classifier.py*")

    return "\n".join(lines)

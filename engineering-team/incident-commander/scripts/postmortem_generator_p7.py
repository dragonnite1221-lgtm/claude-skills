# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p1 import PRIORITY_ORDER, VERSION  # noqa: E402,E501
from postmortem_generator_p4 import PostmortemReport, _bar  # noqa: E402,E501
from postmortem_generator_p5 import _generate_lessons  # noqa: E402,E501
# fmt: on


def format_markdown(report: PostmortemReport) -> str:
    """Format the postmortem as a Markdown document."""
    L: List[str] = []
    inc = report.incident
    L.append(f"# Postmortem: {inc.title}")
    L.append("")
    L.append("| Field | Value |")
    L.append("|-------|-------|")
    L.append(f"| **ID** | {inc.id} |")
    L.append(f"| **Severity** | {inc.severity} |")
    L.append(f"| **Service** | {inc.service} |")
    L.append(f"| **Commander** | {inc.commander} |")
    if inc.affected_services:
        L.append(f"| **Affected Services** | {', '.join(inc.affected_services)} |")
    L.append("")
    # Executive Summary
    L.append("## Executive Summary\n")
    L.append(report.executive_summary())
    L.append("")
    # Timeline Metrics
    L.append("## Timeline Metrics\n")
    L.append("| Metric | Value | Benchmark | Status |")
    L.append("|--------|-------|-----------|--------|")
    labels = {"mttd": "MTTD (Time to Detect)", "mttr": "MTTR (Time to Resolve)",
              "time_to_mitigate": "Time to Mitigate", "time_to_declare": "Time to Declare",
              "postmortem_timeliness": "Postmortem Timeliness"}
    for key, label in labels.items():
        b = report.timeline.benchmark_comparison().get(key)
        if b and "actual_minutes" in b:
            st = "PASS" if b["met_benchmark"] else "FAIL"
            L.append(f"| {label} | {b['actual_minutes']} min | {b['benchmark_minutes']} min | {st} |")
        elif b and "actual_hours" in b:
            st = "PASS" if b["met_target"] else "FAIL"
            L.append(f"| {label} | {b['actual_hours']} hrs | {b['target_hours']} hrs | {st} |")
    L.append("")
    # Customer Impact
    L.append("## Customer Impact\n")
    ci = report.customer_impact_summary()
    L.append(f"- **Affected users:** {ci['affected_users']:,}")
    L.append(f"- **Failed transactions:** {ci['failed_transactions']:,}")
    L.append(f"- **Revenue impact:** ${ci['revenue_impact_usd']:,.2f}")
    L.append(f"- **Data integrity:** {ci['data_integrity']}")
    L.append(f"- **Impact severity:** {ci['impact_severity']}")
    L.append(f"- **Customer communication required:** {'Yes' if ci['customer_communication_required'] else 'No'}")
    L.append("")
    # Root Cause Analysis
    L.append("## Root Cause Analysis\n")
    L.append(f"**Root cause:** {report.resolution.get('root_cause', 'Unknown')}")
    L.append("")
    L.append("### Contributing Factors\n")
    L.append("| # | Category | Weight | Description |")
    L.append("|---|----------|--------|-------------|")
    for i, f in enumerate(report.contributing_factors, 1):
        L.append(f"| {i} | {f.category} | {f.weight:.2f} | {f.description} |")
    L.append("")
    L.append("### Factor Distribution\n")
    L.append("```")
    for cat, pct in sorted(report.factor_distribution.items(), key=lambda x: -x[1]):
        if pct > 0:
            L.append(f"  {cat:<14s} {pct:5.1f}%  {_bar(pct, 25)}")
    L.append("```")
    L.append("")
    # 5-Whys
    L.append("## 5-Whys Analysis\n")
    for analysis in report.five_whys:
        L.append(f"### Factor: {analysis.factor.description}")
        L.append(f"**Systemic theme:** {analysis.systemic_theme}\n")
        for i, step in enumerate(analysis.chain):
            L.append(f"{i}. {step}")
        L.append("")
    L.append("### Theme-Based Recommendations\n")
    for theme, recs in report.theme_recommendations.items():
        L.append(f"**{theme.capitalize()}:**")
        for rec in recs:
            L.append(f"- {rec}")
        L.append("")
    # Mitigation
    L.append("## Mitigation and Resolution\n")
    L.append("### Mitigation Steps Taken\n")
    for step in report.resolution.get("mitigation_steps", []):
        L.append(f"- {step}")
    L.append("")
    L.append("### Permanent Fix\n")
    L.append(report.resolution.get("permanent_fix", "TBD"))
    L.append("")
    # Action Items
    L.append("## Action Items\n")
    L.append("| Priority | Type | Owner | Deadline | Quality | Title |")
    L.append("|----------|------|-------|----------|---------|-------|")
    for a in sorted(report.action_items, key=lambda x: PRIORITY_ORDER.get(x.priority, 99)):
        flag = " **OVERDUE**" if a.is_past_deadline else ""
        L.append(f"| {a.priority} | {a.type} | {a.owner} | {a.deadline} | {a.quality_score}/100 | {a.title}{flag} |")
    L.append("")
    if report.coverage_gaps:
        L.append("### Coverage Gaps\n")
        for gap in report.coverage_gaps:
            L.append(f"> **WARNING:** {gap}")
        L.append("")
    if report.suggested_actions:
        L.append("### Suggested Additional Actions\n")
        for s in report.suggested_actions:
            L.append(f"- **[{s['type'].upper()}]** {s['suggestion']}")
            L.append(f"  - _Reason: {s['reason']}_")
        L.append("")
    overdue = report.overdue_p1_items()
    if overdue:
        L.append("### Overdue P0/P1 Items\n")
        for item in overdue:
            L.append(f"- **{item['title']}** (owner: {item['owner']}, deadline: {item['deadline']})")
        L.append("")
    # Participants
    L.append("## Participants\n")
    L.append("| Name | Role |")
    L.append("|------|------|")
    for p in report.participants:
        L.append(f"| {p.get('name', 'Unknown')} | {p.get('role', '')} |")
    L.append("")
    # Lessons Learned
    L.append("## Lessons Learned\n")
    for i, lesson in enumerate(_generate_lessons(report), 1):
        L.append(f"{i}. {lesson}")
    L.append("")
    L.append("---")
    L.append(f"_Generated by postmortem_generator v{VERSION}_")
    L.append("")
    return "\n".join(L)

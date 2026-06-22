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


def format_text(report: PostmortemReport) -> str:
    """Format the postmortem as plain text."""
    L: List[str] = []
    W = 72

    def h1(title: str) -> None:
        L.append(""); L.append("=" * W); L.append(f"  {title}"); L.append("=" * W)

    def h2(title: str) -> None:
        L.append(""); L.append(f"--- {title} ---")

    inc = report.incident
    h1(f"POSTMORTEM: {inc.title}")
    L.append(f"  ID: {inc.id}  |  Severity: {inc.severity}  |  Service: {inc.service}")
    L.append(f"  Commander: {inc.commander}")
    if inc.affected_services:
        L.append(f"  Affected services: {', '.join(inc.affected_services)}")
    # Executive Summary
    h1("EXECUTIVE SUMMARY")
    L.append("")
    for sentence in report.executive_summary().split(". "):
        s = sentence.strip()
        if s and not s.endswith("."): s += "."
        if s: L.append(f"  {s}")
    # Timeline Metrics
    h1("TIMELINE METRICS")
    tm = report.timeline
    L.append("")
    for label, val, unit in [("MTTD (Time to Detect)", tm.mttd, "min"),
                             ("MTTR (Time to Resolve)", tm.mttr, "min"),
                             ("Time to Mitigate", tm.time_to_mitigate, "min"),
                             ("Time to Declare", tm.time_to_declare, "min"),
                             ("Postmortem Timeliness", tm.postmortem_timeliness_hours, "hrs")]:
        L.append(f"  {label:<30s} {f'{val:.1f} {unit}' if val is not None else 'N/A'}")
    h2("Benchmark Comparison")
    for name, d in tm.benchmark_comparison().items():
        if "actual_minutes" in d:
            st = "PASS" if d["met_benchmark"] else "FAIL"
            L.append(f"  {name:<25s} actual={d['actual_minutes']}min  benchmark={d['benchmark_minutes']}min  [{st}]")
        elif "actual_hours" in d:
            st = "PASS" if d["met_target"] else "FAIL"
            L.append(f"  {name:<25s} actual={d['actual_hours']}hrs  target={d['target_hours']}hrs  [{st}]")
    # Customer Impact
    h1("CUSTOMER IMPACT")
    ci = report.customer_impact_summary()
    L.append("")
    L.append(f"  Affected users:          {ci['affected_users']:,}")
    L.append(f"  Failed transactions:     {ci['failed_transactions']:,}")
    L.append(f"  Revenue impact:          ${ci['revenue_impact_usd']:,.2f}")
    L.append(f"  Data integrity:          {ci['data_integrity']}")
    L.append(f"  Impact severity:         {ci['impact_severity']}")
    L.append(f"  Comms required:          {'Yes' if ci['customer_communication_required'] else 'No'}")
    # Root Cause
    h1("ROOT CAUSE ANALYSIS")
    L.append("")
    L.append(f"  {report.resolution.get('root_cause', 'Unknown')}")
    h2("Contributing Factors")
    for f in report.contributing_factors:
        L.append(f"  [{f.category.upper():<12s} w={f.weight:.2f}] {f.description}")
    h2("Factor Distribution")
    for cat, pct in sorted(report.factor_distribution.items(), key=lambda x: -x[1]):
        if pct > 0:
            L.append(f"  {cat:<14s} {pct:5.1f}%  {_bar(pct)}")
    # 5-Whys
    h1("5-WHYS ANALYSIS")
    for analysis in report.five_whys:
        L.append("")
        L.append(f"  Factor: {analysis.factor.description}")
        L.append(f"  Theme:  {analysis.systemic_theme}")
        for i, step in enumerate(analysis.chain):
            L.append(f"    {i}. {step}")
    h2("Theme-Based Recommendations")
    for theme, recs in report.theme_recommendations.items():
        L.append(f"  [{theme.upper()}]")
        for rec in recs:
            L.append(f"    - {rec}")
    # Mitigation & Fix
    h1("MITIGATION AND RESOLUTION")
    h2("Mitigation Steps Taken")
    for step in report.resolution.get("mitigation_steps", []):
        L.append(f"  - {step}")
    h2("Permanent Fix")
    L.append(f"  {report.resolution.get('permanent_fix', 'TBD')}")
    # Action Items
    h1("ACTION ITEMS")
    L.append("")
    hdr = f"  {'Priority':<10s} {'Type':<14s} {'Owner':<25s} {'Deadline':<12s} {'Quality':<8s} Title"
    L.append(hdr)
    L.append("  " + "-" * (len(hdr) - 2))
    for a in sorted(report.action_items, key=lambda x: PRIORITY_ORDER.get(x.priority, 99)):
        flag = " *OVERDUE*" if a.is_past_deadline else ""
        L.append(f"  {a.priority:<10s} {a.type:<14s} {a.owner:<25s} {a.deadline:<12s} "
                 f"{a.quality_score:<8d} {a.title}{flag}")
    if report.coverage_gaps:
        h2("Coverage Gaps")
        for gap in report.coverage_gaps:
            L.append(f"  WARNING: {gap}")
    if report.suggested_actions:
        h2("Suggested Additional Actions")
        for s in report.suggested_actions:
            L.append(f"  [{s['type'].upper()}] {s['suggestion']}")
            L.append(f"    Reason: {s['reason']}")
    overdue = report.overdue_p1_items()
    if overdue:
        h2("Overdue P0/P1 Items")
        for item in overdue:
            L.append(f"  OVERDUE: {item['title']} (owner: {item['owner']}, deadline: {item['deadline']})")
    # Participants
    h1("PARTICIPANTS")
    L.append("")
    for p in report.participants:
        L.append(f"  {p.get('name', 'Unknown'):<25s} {p.get('role', '')}")
    # Lessons Learned
    h1("LESSONS LEARNED")
    L.append("")
    for i, lesson in enumerate(_generate_lessons(report), 1):
        L.append(f"  {i}. {lesson}")
    L.append("")
    L.append("=" * W)
    L.append(f"  Generated by postmortem_generator v{VERSION}")
    L.append("=" * W)
    L.append("")
    return "\n".join(L)
def format_json(report: PostmortemReport) -> str:
    """Format the postmortem as JSON."""
    data = report.to_dict()
    data["lessons_learned"] = _generate_lessons(report)
    return json.dumps(data, indent=2, default=str)

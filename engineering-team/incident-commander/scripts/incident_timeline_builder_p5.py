# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402
# fmt: off
from incident_timeline_builder_p1 import GAP_THRESHOLD_MINUTES, TimelineAnalysis  # noqa: E402,E501
from incident_timeline_builder_p2 import _fmt_duration, _fmt_ts, _sev_label  # noqa: E402,E501
# fmt: on


def format_markdown_output(analysis: TimelineAnalysis) -> str:
    """Format the analysis as a professional Markdown report."""
    L: List[str] = []

    L.append(f"# Incident Timeline Report: {analysis.incident_id}")
    L.append("")

    if analysis.errors:
        L.append("> **Warnings:**")
        for err in analysis.errors:
            L.append(f"> - {err}")
        L.append("")
        if not analysis.events:
            return "\n".join(L)

    # Summary table
    L.append("## Incident Summary")
    L.append("")
    L.append("| Field | Value |")
    L.append("|-------|-------|")
    L.append(f"| **ID** | {analysis.incident_id} |")
    L.append(f"| **Title** | {analysis.incident_title} |")
    L.append(f"| **Severity** | {analysis.severity} ({_sev_label(analysis.severity)}) |")
    L.append(f"| **Status** | {analysis.status.capitalize()} |")
    L.append(f"| **Commander** | {analysis.commander} |")
    L.append(f"| **Service** | {analysis.service} |")
    if analysis.affected_services:
        L.append(f"| **Affected Services** | {', '.join(analysis.affected_services)} |")
    L.append(f"| **Duration** | {_fmt_duration(analysis.metrics.get('total_duration_minutes'))} |")
    L.append("")

    # Key metrics
    L.append("## Key Metrics")
    L.append("")
    L.append(f"- **MTTD (Mean Time to Detect):** {_fmt_duration(analysis.metrics.get('mttd_minutes'))}")
    L.append(f"- **MTTR (Mean Time to Resolve):** {_fmt_duration(analysis.metrics.get('mttr_minutes'))}")
    L.append(f"- **Total Events:** {analysis.metrics.get('total_events', 0)}")
    L.append(f"- **Decision Points:** {analysis.metrics.get('decision_point_count', 0)}")
    L.append(f"- **Timeline Gaps (>{GAP_THRESHOLD_MINUTES}m):** {analysis.metrics.get('gap_count', 0)}")
    if analysis.metrics.get("longest_gap_minutes", 0) > 0:
        L.append(f"- **Longest Gap:** {_fmt_duration(analysis.metrics.get('longest_gap_minutes'))}")
    L.append("")

    # Phases table
    L.append("## Incident Phases")
    L.append("")
    if analysis.phases:
        L.append("| Phase | Start | End | Duration | Events |")
        L.append("|-------|-------|-----|----------|--------|")
        for p in analysis.phases:
            L.append(f"| {p.name} | {_fmt_ts(p.start_time)} | {_fmt_ts(p.end_time)} | {_fmt_duration(p.duration_minutes)} | {len(p.events)} |")
        L.append("")
        # ASCII bar chart
        max_dur = max((p.duration_minutes for p in analysis.phases if p.duration_minutes), default=0)
        if max_dur and max_dur > 0:
            L.append("### Phase Duration Distribution")
            L.append("")
            L.append("```")
            for p in analysis.phases:
                d = p.duration_minutes or 0
                bar = "#" * int((d / max_dur) * 40)
                L.append(f"  {p.name:15s} |{bar} {_fmt_duration(d)}")
            L.append("```")
            L.append("")
    else:
        L.append("No phases detected.")
        L.append("")

    # Chronological timeline
    L.append("## Chronological Timeline")
    L.append("")
    for e in analysis.events:
        dm = " **[KEY DECISION]**" if e.is_decision_point else ""
        L.append(f"- `{_fmt_ts(e.timestamp)}` **{e.type.upper()}** ({e.actor}){dm}")
        L.append(f"  - {e.description}")
    L.append("")

    # Gap analysis
    if analysis.gaps:
        L.append("## Gap Analysis")
        L.append("")
        L.append(f"> {len(analysis.gaps)} gap(s) of >{GAP_THRESHOLD_MINUTES} minutes detected. "
                 f"These may represent blind spots where important activity was not recorded.")
        L.append("")
        for g in analysis.gaps:
            L.append(f"- **{_fmt_duration(g.duration_minutes)}** gap from `{_fmt_ts(g.start)}` to `{_fmt_ts(g.end)}`")
        L.append("")

    # Decision points
    if analysis.decision_points:
        L.append("## Key Decision Points")
        L.append("")
        for dp in analysis.decision_points:
            L.append(f"1. `{_fmt_ts(dp.timestamp)}` **{dp.type.upper()}** - {dp.description}")
        L.append("")

    # Communications
    if analysis.communications:
        L.append("## Generated Communications")
        L.append("")
        for c in analysis.communications:
            L.append(f"### {c.template_type.replace('_', ' ').title()} ({c.audience})")
            L.append("")
            L.append(f"**Subject:** {c.subject}")
            L.append("")
            for bl in c.body.split("\n"):
                L.append(bl)
            L.append("")
            L.append("---")
            L.append("")

    # Event type breakdown
    tc = analysis.metrics.get("event_counts_by_type", {})
    if tc:
        L.append("## Event Type Breakdown")
        L.append("")
        L.append("| Type | Count |")
        L.append("|------|-------|")
        for etype, count in sorted(tc.items(), key=lambda x: -x[1]):
            L.append(f"| {etype} | {count} |")
        L.append("")

    L.append("---")
    L.append(f"*Report generated for incident {analysis.incident_id}. All timestamps in UTC.*")
    return "\n".join(L)

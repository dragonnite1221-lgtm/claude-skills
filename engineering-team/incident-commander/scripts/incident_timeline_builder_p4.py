# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402
# fmt: off
from incident_timeline_builder_p1 import GAP_THRESHOLD_MINUTES, ISO_FORMAT, TimelineAnalysis  # noqa: E402,E501
from incident_timeline_builder_p2 import _fmt_duration, _fmt_ts  # noqa: E402,E501
# fmt: on


def format_text_output(analysis: TimelineAnalysis) -> str:
    """Format the analysis as a human-readable text report."""
    L: List[str] = []
    w = 64

    L.append("=" * w)
    L.append("INCIDENT TIMELINE REPORT")
    L.append("=" * w)
    L.append("")

    if analysis.errors:
        for err in analysis.errors:
            L.append(f"  WARNING: {err}")
        L.append("")
        if not analysis.events:
            return "\n".join(L)

    # Summary
    L.append("INCIDENT SUMMARY")
    L.append("-" * 32)
    L.append(f"  ID:         {analysis.incident_id}")
    L.append(f"  Title:      {analysis.incident_title}")
    L.append(f"  Severity:   {analysis.severity}")
    L.append(f"  Status:     {analysis.status.capitalize()}")
    L.append(f"  Commander:  {analysis.commander}")
    L.append(f"  Service:    {analysis.service}")
    if analysis.affected_services:
        L.append(f"  Affected:   {', '.join(analysis.affected_services)}")
    L.append(f"  Duration:   {_fmt_duration(analysis.metrics.get('total_duration_minutes'))}")
    L.append("")

    # Key metrics
    L.append("KEY METRICS")
    L.append("-" * 32)
    L.append(f"  MTTD (Mean Time to Detect):   {_fmt_duration(analysis.metrics.get('mttd_minutes'))}")
    L.append(f"  MTTR (Mean Time to Resolve):  {_fmt_duration(analysis.metrics.get('mttr_minutes'))}")
    L.append(f"  Total Events:                 {analysis.metrics.get('total_events', 0)}")
    L.append(f"  Decision Points:              {analysis.metrics.get('decision_point_count', 0)}")
    L.append(f"  Timeline Gaps (>{GAP_THRESHOLD_MINUTES}m):      {analysis.metrics.get('gap_count', 0)}")
    L.append("")

    # Phases
    L.append("INCIDENT PHASES")
    L.append("-" * 32)
    if analysis.phases:
        for p in analysis.phases:
            L.append(f"  [{_fmt_ts(p.start_time)} - {_fmt_ts(p.end_time)}]  {p.name} ({_fmt_duration(p.duration_minutes)})")
            L.append(f"    {p.description}")
            L.append(f"    Events: {len(p.events)}")
    else:
        L.append("  No phases detected.")
    L.append("")

    # Chronological timeline
    L.append("CHRONOLOGICAL TIMELINE")
    L.append("-" * 32)
    for e in analysis.events:
        marker = "*" if e.is_decision_point else " "
        L.append(f"  {_fmt_ts(e.timestamp)} {marker} [{e.type.upper():13s}] {e.actor}")
        L.append(f"             {e.description}")
    L.append("")
    L.append("  (* = key decision point)")
    L.append("")

    # Gap warnings
    if analysis.gaps:
        L.append("GAP ANALYSIS")
        L.append("-" * 32)
        for g in analysis.gaps:
            L.append(f"  WARNING: {_fmt_duration(g.duration_minutes)} gap between {_fmt_ts(g.start)} and {_fmt_ts(g.end)}")
        L.append("")

    # Decision points
    if analysis.decision_points:
        L.append("KEY DECISION POINTS")
        L.append("-" * 32)
        for dp in analysis.decision_points:
            L.append(f"  {_fmt_ts(dp.timestamp)}  [{dp.type.upper()}] {dp.description}")
        L.append("")

    # Communications
    if analysis.communications:
        L.append("GENERATED COMMUNICATIONS")
        L.append("-" * 32)
        for c in analysis.communications:
            L.append(f"  Type:     {c.template_type}")
            L.append(f"  Audience: {c.audience}")
            L.append(f"  Subject:  {c.subject}")
            L.append("  ---")
            for bl in c.body.split("\n"):
                L.append(f"  {bl}")
            L.append("")

    L.append("=" * w)
    L.append("END OF REPORT")
    L.append("=" * w)
    return "\n".join(L)
def format_json_output(analysis: TimelineAnalysis) -> Dict[str, Any]:
    """Format the analysis as a structured JSON-serializable dictionary."""
    return {
        "incident": {
            "id": analysis.incident_id, "title": analysis.incident_title,
            "severity": analysis.severity, "status": analysis.status,
            "commander": analysis.commander, "service": analysis.service,
            "affected_services": analysis.affected_services,
            "declared_at": analysis.declared_at.strftime(ISO_FORMAT) if analysis.declared_at else None,
            "resolved_at": analysis.resolved_at.strftime(ISO_FORMAT) if analysis.resolved_at else None,
        },
        "timeline": [e.to_dict() for e in analysis.events],
        "phases": [p.to_dict() for p in analysis.phases],
        "gaps": [g.to_dict() for g in analysis.gaps],
        "decision_points": [e.to_dict() for e in analysis.decision_points],
        "metrics": analysis.metrics,
        "communications": [c.to_dict() for c in analysis.communications],
        "errors": analysis.errors if analysis.errors else [],
    }

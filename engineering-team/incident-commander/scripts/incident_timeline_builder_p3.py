# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402
# fmt: off
from incident_timeline_builder_p1 import CommunicationTemplate, TimelineAnalysis  # noqa: E402,E501
from incident_timeline_builder_p2 import _fmt_duration, _sev_label, detect_gaps, detect_phases, identify_decision_points, parse_incident_data  # noqa: E402,E501
# fmt: on


def calculate_metrics(analysis: TimelineAnalysis) -> None:
    """Calculate incident response metrics: MTTD, MTTR, phase durations."""
    m: Dict[str, Any] = {}
    det = [e for e in analysis.events if e.type == "detection"]
    first_det = det[0].timestamp if det else None
    first_ts = analysis.events[0].timestamp if analysis.events else None

    # MTTD: first event to first detection.
    if first_ts and first_det:
        m["mttd_minutes"] = round((first_det - first_ts).total_seconds() / 60.0, 1)
    else:
        m["mttd_minutes"] = None

    # MTTR: detection to resolution.
    if first_det and analysis.resolved_at:
        m["mttr_minutes"] = round((analysis.resolved_at - first_det).total_seconds() / 60.0, 1)
    else:
        m["mttr_minutes"] = None

    # Total duration.
    if analysis.declared_at and analysis.resolved_at:
        m["total_duration_minutes"] = round(
            (analysis.resolved_at - analysis.declared_at).total_seconds() / 60.0, 1)
    else:
        m["total_duration_minutes"] = None

    # Phase durations.
    m["phase_durations"] = {
        p.name: (round(p.duration_minutes, 1) if p.duration_minutes is not None else None)
        for p in analysis.phases
    }

    # Event counts by type.
    tc: Dict[str, int] = {}
    for e in analysis.events:
        tc[e.type] = tc.get(e.type, 0) + 1
    m["event_counts_by_type"] = tc

    # Gap statistics.
    m["gap_count"] = len(analysis.gaps)
    if analysis.gaps:
        gm = [g.duration_minutes for g in analysis.gaps]
        m["longest_gap_minutes"] = round(max(gm), 1)
        m["total_gap_minutes"] = round(sum(gm), 1)
    else:
        m["longest_gap_minutes"] = 0
        m["total_gap_minutes"] = 0

    m["total_events"] = len(analysis.events)
    m["decision_point_count"] = len(analysis.decision_points)
    m["phase_count"] = len(analysis.phases)
    analysis.metrics = m
def generate_communications(analysis: TimelineAnalysis) -> None:
    """Generate four communication templates based on incident data."""
    sev, sl = analysis.severity, _sev_label(analysis.severity)
    title, svc = analysis.incident_title, analysis.service
    affected = ", ".join(analysis.affected_services) or "none identified"
    cmd, iid = analysis.commander, analysis.incident_id
    decl = analysis.declared_at.strftime("%Y-%m-%d %H:%M UTC") if analysis.declared_at else "TBD"
    resv = analysis.resolved_at.strftime("%Y-%m-%d %H:%M UTC") if analysis.resolved_at else "TBD"
    dur = _fmt_duration(analysis.metrics.get("total_duration_minutes"))
    resolved = analysis.status == "resolved"

    # 1 -- Initial stakeholder notification
    analysis.communications.append(CommunicationTemplate(
        "initial_notification", "internal", f"[{sev}] Incident Declared: {title}",
        f"An incident has been declared for {svc}.\n\n"
        f"Incident ID: {iid}\nSeverity: {sev} ({sl})\nCommander: {cmd}\n"
        f"Declared at: {decl}\nAffected services: {affected}\n\n"
        f"The incident team is actively investigating. Updates will follow.",
    ))

    # 2 -- Status page update
    if resolved:
        sp_subj = f"[Resolved] {title}"
        sp_body = (f"The incident affecting {svc} has been resolved.\n\n"
                   f"Duration: {dur}\nAll affected services ({affected}) are restored. "
                   f"A post-incident review will be published within 48 hours.")
    else:
        sp_subj = f"[Investigating] {title}"
        sp_body = (f"We are investigating degraded performance in {svc}. "
                   f"Affected services: {affected}.\n\n"
                   f"Our team is working to identify the root cause. Updates every 30 minutes.")
    analysis.communications.append(CommunicationTemplate(
        "status_page", "external", sp_subj, sp_body))

    # 3 -- Executive summary
    phase_lines = "\n".join(
        f"  - {p.name}: {_fmt_duration(p.duration_minutes)}" for p in analysis.phases
    ) or "  No phase data available."
    mttd = _fmt_duration(analysis.metrics.get("mttd_minutes"))
    mttr = _fmt_duration(analysis.metrics.get("mttr_minutes"))
    analysis.communications.append(CommunicationTemplate(
        "executive_summary", "executive", f"Executive Summary: {iid} - {title}",
        f"Incident: {iid} - {title}\nSeverity: {sev} ({sl})\n"
        f"Service: {svc}\nCommander: {cmd}\nStatus: {analysis.status.capitalize()}\n"
        f"Declared: {decl}\nResolved: {resv}\nDuration: {dur}\n\n"
        f"Key Metrics:\n  - MTTD: {mttd}\n  - MTTR: {mttr}\n"
        f"  - Timeline Gaps: {analysis.metrics.get('gap_count', 0)}\n\n"
        f"Phase Breakdown:\n{phase_lines}\n\nAffected Services: {affected}",
    ))

    # 4 -- Customer notification
    if resolved:
        cust_body = (f"We experienced an issue affecting {svc} starting at {decl}.\n\n"
                     f"The issue was resolved at {resv} (duration: {dur}). "
                     f"We apologize for any inconvenience and are reviewing to prevent recurrence.")
    else:
        cust_body = (f"We are experiencing an issue affecting {svc} starting at {decl}.\n\n"
                     f"Our engineering team is actively working to resolve this. "
                     f"We will provide updates as the situation develops. We apologize for the inconvenience.")
    analysis.communications.append(CommunicationTemplate(
        "customer_notification", "external", f"Service Update: {title}", cust_body))
def build_timeline(data: Dict[str, Any]) -> TimelineAnalysis:
    """Run the full timeline analysis pipeline on raw incident data."""
    analysis = parse_incident_data(data)
    if analysis.errors and not analysis.events:
        return analysis
    detect_phases(analysis)
    detect_gaps(analysis)
    identify_decision_points(analysis)
    calculate_metrics(analysis)
    generate_communications(analysis)
    return analysis

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402
# fmt: off
from incident_timeline_builder_p1 import GAP_THRESHOLD_MINUTES, IncidentEvent, IncidentPhase, PHASE_DEFINITIONS, SEVERITY_LEVELS, TimelineAnalysis, TimelineGap, _parse_timestamp  # noqa: E402,E501
# fmt: on


def _fmt_duration(minutes: Optional[float]) -> str:
    """Format a duration in minutes as a human-readable string."""
    if minutes is None:
        return "N/A"
    if minutes < 1:
        return f"{minutes * 60:.0f}s"
    if minutes < 60:
        return f"{minutes:.0f}m"
    hours, remaining = int(minutes // 60), int(minutes % 60)
    return f"{hours}h" if remaining == 0 else f"{hours}h {remaining}m"
def _fmt_ts(dt: Optional[datetime]) -> str:
    """Format a datetime as HH:MM:SS for display."""
    return dt.strftime("%H:%M:%S") if dt else "??:??:??"
def _sev_label(sev: str) -> str:
    """Return the human label for a severity code."""
    return SEVERITY_LEVELS.get(sev, {}).get("label", sev)
def parse_incident_data(data: Dict[str, Any]) -> TimelineAnalysis:
    """Parse raw incident JSON into a TimelineAnalysis with populated fields."""
    a = TimelineAnalysis()
    inc = data.get("incident", {})
    a.incident_id = inc.get("id", "UNKNOWN")
    a.incident_title = inc.get("title", "Untitled Incident")
    a.severity = inc.get("severity", "UNKNOWN").upper()
    a.status = inc.get("status", "unknown").lower()
    a.commander = inc.get("commander", "Unassigned")
    a.service = inc.get("service", "unknown")
    a.affected_services = inc.get("affected_services", [])
    a.declared_at = _parse_timestamp(inc.get("declared_at", ""))
    a.resolved_at = _parse_timestamp(inc.get("resolved_at", ""))

    raw_events = data.get("events", [])
    if not raw_events:
        a.errors.append("No events found in incident data.")
        return a

    for raw in raw_events:
        event = IncidentEvent(raw)
        if event.timestamp is None:
            a.errors.append(f"Skipping event with unparseable timestamp: {raw.get('timestamp', '')}")
            continue
        a.events.append(event)

    a.events.sort(key=lambda e: e.timestamp)  # type: ignore[arg-type]
    return a
def detect_phases(analysis: TimelineAnalysis) -> None:
    """Detect incident lifecycle phases from the ordered event stream."""
    if not analysis.events:
        return

    trigger_map: Dict[str, Dict[str, str]] = {}
    for pdef in PHASE_DEFINITIONS:
        for ttype in pdef["trigger_types"]:
            trigger_map[ttype] = {"name": pdef["name"], "description": pdef["description"]}

    phase_by_name: Dict[str, IncidentPhase] = {}
    phase_order: List[str] = []
    current: Optional[IncidentPhase] = None

    for event in analysis.events:
        pinfo = trigger_map.get(event.type)
        if pinfo and pinfo["name"] not in phase_by_name:
            if current is not None:
                current.end_time = event.timestamp
            phase = IncidentPhase(pinfo["name"], pinfo["description"])
            phase.start_time = event.timestamp
            phase_by_name[pinfo["name"]] = phase
            phase_order.append(pinfo["name"])
            current = phase
        if current is not None:
            current.events.append(event)

    if current is not None:
        current.end_time = analysis.resolved_at or analysis.events[-1].timestamp

    analysis.phases = [phase_by_name[n] for n in phase_order]
def detect_gaps(analysis: TimelineAnalysis) -> None:
    """Identify gaps longer than GAP_THRESHOLD_MINUTES between consecutive events."""
    for i in range(len(analysis.events) - 1):
        ts_a, ts_b = analysis.events[i].timestamp, analysis.events[i + 1].timestamp
        if ts_a is None or ts_b is None:
            continue
        delta = (ts_b - ts_a).total_seconds() / 60.0
        if delta >= GAP_THRESHOLD_MINUTES:
            analysis.gaps.append(TimelineGap(start=ts_a, end=ts_b, duration_minutes=delta))
def identify_decision_points(analysis: TimelineAnalysis) -> None:
    """Extract key decision-point events from the timeline."""
    analysis.decision_points = [e for e in analysis.events if e.is_decision_point]

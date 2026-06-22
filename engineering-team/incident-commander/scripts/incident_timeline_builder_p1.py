# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_timeline_builder_base import *  # noqa: F403,E402


ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
EVENT_TYPES = [
    "detection", "declaration", "escalation", "investigation",
    "mitigation", "communication", "resolution", "action_item",
]
SEVERITY_LEVELS = {
    "SEV1": {"label": "Critical", "rank": 1},
    "SEV2": {"label": "Major", "rank": 2},
    "SEV3": {"label": "Minor", "rank": 3},
    "SEV4": {"label": "Low", "rank": 4},
}
PHASE_DEFINITIONS = [
    {"name": "Detection", "trigger_types": ["detection"],
     "description": "Issue detected via monitoring, alerting, or user report."},
    {"name": "Triage", "trigger_types": ["declaration", "escalation"],
     "description": "Incident declared, severity assessed, commander assigned."},
    {"name": "Investigation", "trigger_types": ["investigation"],
     "description": "Root cause analysis and impact assessment underway."},
    {"name": "Mitigation", "trigger_types": ["mitigation"],
     "description": "Active work to reduce or eliminate customer impact."},
    {"name": "Resolution", "trigger_types": ["resolution"],
     "description": "Service restored to normal operating parameters."},
]
GAP_THRESHOLD_MINUTES = 15
DECISION_EVENT_TYPES = {"escalation", "mitigation", "declaration", "resolution"}
def _parse_timestamp(raw: str) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string into a datetime object."""
    if not raw:
        return None
    cleaned = raw.replace("Z", "+00:00") if raw.endswith("Z") else raw
    try:
        return datetime.fromisoformat(cleaned).replace(tzinfo=None)
    except (ValueError, AttributeError):
        pass
    try:
        return datetime.strptime(raw, ISO_FORMAT)
    except ValueError:
        return None
class IncidentEvent:
    """Represents a single event in the incident timeline."""

    def __init__(self, data: Dict[str, Any]):
        self.timestamp_raw: str = data.get("timestamp", "")
        self.timestamp: Optional[datetime] = _parse_timestamp(self.timestamp_raw)
        self.type: str = data.get("type", "unknown").lower().strip()
        self.actor: str = data.get("actor", "unknown")
        self.description: str = data.get("description", "")
        self.metadata: Dict[str, Any] = data.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "timestamp": self.timestamp_raw, "type": self.type,
            "actor": self.actor, "description": self.description,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @property
    def is_decision_point(self) -> bool:
        return self.type in DECISION_EVENT_TYPES
class IncidentPhase:
    """Represents a detected phase of the incident lifecycle."""

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.events: List[IncidentEvent] = []

    @property
    def duration_minutes(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60.0
        return None

    def to_dict(self) -> Dict[str, Any]:
        dur = self.duration_minutes
        return {
            "name": self.name, "description": self.description,
            "start_time": self.start_time.strftime(ISO_FORMAT) if self.start_time else None,
            "end_time": self.end_time.strftime(ISO_FORMAT) if self.end_time else None,
            "duration_minutes": round(dur, 1) if dur is not None else None,
            "event_count": len(self.events),
        }
class CommunicationTemplate:
    """A generated communication message for a specific audience."""

    def __init__(self, template_type: str, audience: str, subject: str, body: str):
        self.template_type = template_type
        self.audience = audience
        self.subject = subject
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {"template_type": self.template_type, "audience": self.audience,
                "subject": self.subject, "body": self.body}
class TimelineGap:
    """Represents a gap in the timeline where no events were logged."""

    def __init__(self, start: datetime, end: datetime, duration_minutes: float):
        self.start = start
        self.end = end
        self.duration_minutes = duration_minutes

    def to_dict(self) -> Dict[str, Any]:
        return {"start": self.start.strftime(ISO_FORMAT),
                "end": self.end.strftime(ISO_FORMAT),
                "duration_minutes": round(self.duration_minutes, 1)}
class TimelineAnalysis:
    """Holds the complete analysis result for an incident timeline."""

    def __init__(self):
        self.incident_id: str = ""
        self.incident_title: str = ""
        self.severity: str = ""
        self.status: str = ""
        self.commander: str = ""
        self.service: str = ""
        self.affected_services: List[str] = []
        self.declared_at: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None
        self.events: List[IncidentEvent] = []
        self.phases: List[IncidentPhase] = []
        self.gaps: List[TimelineGap] = []
        self.decision_points: List[IncidentEvent] = []
        self.metrics: Dict[str, Any] = {}
        self.communications: List[CommunicationTemplate] = []
        self.errors: List[str] = []

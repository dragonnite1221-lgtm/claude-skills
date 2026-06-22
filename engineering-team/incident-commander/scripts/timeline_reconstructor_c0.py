# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin0:
    """
    Reconstructs incident timelines from disparate event sources.
    Identifies phases, calculates metrics, and performs gap analysis.
    """
    def __init__(self):
        """Initialize the reconstructor with phase detection rules and templates."""
        self.phase_patterns = self._load_phase_patterns()
        self.event_types = self._load_event_types()
        self.severity_mapping = self._load_severity_mapping()
        self.gap_thresholds = self._load_gap_thresholds()
    def _load_phase_patterns(self) -> Dict[str, Dict]:
        """Load patterns for identifying incident phases."""
        return {
            "detection": {
                "keywords": [
                    "alert", "alarm", "triggered", "fired", "detected", "noticed",
                    "monitoring", "threshold exceeded", "anomaly", "spike",
                    "error rate", "latency increase", "timeout", "failure"
                ],
                "event_types": ["alert", "monitoring", "notification"],
                "priority": 1,
                "description": "Initial detection of the incident through monitoring or observation"
            },
            "triage": {
                "keywords": [
                    "investigating", "triaging", "assessing", "evaluating",
                    "checking", "looking into", "analyzing", "reviewing",
                    "diagnosis", "troubleshooting", "examining"
                ],
                "event_types": ["investigation", "communication", "action"],
                "priority": 2,
                "description": "Assessment and initial investigation of the incident"
            },
            "escalation": {
                "keywords": [
                    "escalating", "paging", "calling in", "requesting help",
                    "engaging", "involving", "notifying", "alerting team",
                    "incident commander", "war room", "all hands"
                ],
                "event_types": ["escalation", "communication", "notification"],
                "priority": 3,
                "description": "Escalation to additional resources or higher severity response"
            },
            "mitigation": {
                "keywords": [
                    "fixing", "patching", "deploying", "rolling back", "restarting",
                    "scaling", "rerouting", "bypassing", "workaround",
                    "implementing fix", "applying solution", "remediation"
                ],
                "event_types": ["deployment", "action", "fix"],
                "priority": 4,
                "description": "Active mitigation efforts to resolve the incident"
            },
            "resolution": {
                "keywords": [
                    "resolved", "fixed", "restored", "recovered", "back online",
                    "working", "normal", "stable", "healthy", "operational",
                    "incident closed", "service restored"
                ],
                "event_types": ["resolution", "confirmation"],
                "priority": 5,
                "description": "Confirmation that the incident has been resolved"
            },
            "review": {
                "keywords": [
                    "post-mortem", "retrospective", "review", "lessons learned",
                    "pir", "post-incident", "analysis", "follow-up",
                    "action items", "improvements"
                ],
                "event_types": ["review", "documentation"],
                "priority": 6,
                "description": "Post-incident review and documentation activities"
            }
        }
    def _load_event_types(self) -> Dict[str, Dict]:
        """Load event type classification rules."""
        return {
            "alert": {
                "sources": ["monitoring", "nagios", "datadog", "newrelic", "prometheus"],
                "indicators": ["alert", "alarm", "threshold", "metric"],
                "severity_boost": 2
            },
            "log": {
                "sources": ["application", "server", "container", "system"],
                "indicators": ["error", "exception", "warn", "fail"],
                "severity_boost": 1
            },
            "communication": {
                "sources": ["slack", "teams", "email", "chat"],
                "indicators": ["message", "notification", "update"],
                "severity_boost": 0
            },
            "deployment": {
                "sources": ["ci/cd", "jenkins", "github", "gitlab", "deploy"],
                "indicators": ["deploy", "release", "build", "merge"],
                "severity_boost": 3
            },
            "action": {
                "sources": ["manual", "script", "automation", "operator"],
                "indicators": ["executed", "ran", "performed", "applied"],
                "severity_boost": 2
            },
            "escalation": {
                "sources": ["pagerduty", "opsgenie", "oncall", "escalation"],
                "indicators": ["paged", "escalated", "notified", "assigned"],
                "severity_boost": 3
            }
        }

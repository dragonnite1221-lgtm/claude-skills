# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin2:
    def _load_action_templates(self) -> Dict[str, List[Dict]]:
        """Load initial action templates for each severity level."""
        return {
            "sev1": [
                {
                    "action": "Establish incident command",
                    "priority": 1,
                    "timeout_minutes": 5,
                    "description": "Page incident commander and establish war room"
                },
                {
                    "action": "Create incident ticket",
                    "priority": 1,
                    "timeout_minutes": 2,
                    "description": "Create tracking ticket with all known details"
                },
                {
                    "action": "Update status page",
                    "priority": 2,
                    "timeout_minutes": 15,
                    "description": "Post initial status page update acknowledging incident"
                },
                {
                    "action": "Notify executives",
                    "priority": 2,
                    "timeout_minutes": 15,
                    "description": "Alert executive team of customer-impacting outage"
                },
                {
                    "action": "Engage subject matter experts",
                    "priority": 3,
                    "timeout_minutes": 10,
                    "description": "Page relevant SMEs based on affected systems"
                },
                {
                    "action": "Begin technical investigation",
                    "priority": 3,
                    "timeout_minutes": 5,
                    "description": "Start technical diagnosis and mitigation efforts"
                }
            ],
            "sev2": [
                {
                    "action": "Assign incident commander",
                    "priority": 1,
                    "timeout_minutes": 30,
                    "description": "Assign IC and establish coordination channel"
                },
                {
                    "action": "Create incident tracking",
                    "priority": 1,
                    "timeout_minutes": 5,
                    "description": "Create incident ticket with details and timeline"
                },
                {
                    "action": "Assess customer impact",
                    "priority": 2,
                    "timeout_minutes": 15,
                    "description": "Determine scope and severity of user impact"
                },
                {
                    "action": "Engage response team",
                    "priority": 2,
                    "timeout_minutes": 30,
                    "description": "Page appropriate technical responders"
                },
                {
                    "action": "Begin investigation",
                    "priority": 3,
                    "timeout_minutes": 15,
                    "description": "Start technical analysis and debugging"
                },
                {
                    "action": "Plan status communication",
                    "priority": 3,
                    "timeout_minutes": 30,
                    "description": "Determine if status page update is needed"
                }
            ],
            "sev3": [
                {
                    "action": "Assign to appropriate team",
                    "priority": 1,
                    "timeout_minutes": 120,
                    "description": "Route to team with relevant expertise"
                },
                {
                    "action": "Create tracking ticket",
                    "priority": 1,
                    "timeout_minutes": 30,
                    "description": "Document issue in standard ticketing system"
                },
                {
                    "action": "Assess scope and impact",
                    "priority": 2,
                    "timeout_minutes": 60,
                    "description": "Understand full scope of the issue"
                },
                {
                    "action": "Identify workarounds",
                    "priority": 2,
                    "timeout_minutes": 60,
                    "description": "Find temporary solutions if possible"
                },
                {
                    "action": "Plan resolution approach",
                    "priority": 3,
                    "timeout_minutes": 120,
                    "description": "Develop plan for permanent fix"
                }
            ],
            "sev4": [
                {
                    "action": "Create backlog item",
                    "priority": 1,
                    "timeout_minutes": 1440,  # 24 hours
                    "description": "Add to team backlog for future sprint planning"
                },
                {
                    "action": "Triage and prioritize",
                    "priority": 2,
                    "timeout_minutes": 2880,  # 2 days
                    "description": "Review and prioritize against other work"
                },
                {
                    "action": "Assign owner",
                    "priority": 3,
                    "timeout_minutes": 4320,  # 3 days
                    "description": "Assign to appropriate developer when capacity allows"
                }
            ]
        }

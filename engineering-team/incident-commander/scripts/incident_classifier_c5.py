# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin5:
    def _generate_timeline(self, severity: str) -> Dict:
        """Generate expected response timeline."""
        rules = self.severity_rules[severity]
        now = datetime.now(timezone.utc)
        
        milestones = []
        if severity == "sev1":
            milestones = [
                {"milestone": "Incident Commander assigned", "minutes": 5},
                {"milestone": "War room established", "minutes": 10},
                {"milestone": "Initial status page update", "minutes": 15},
                {"milestone": "Executive notification", "minutes": 15},
                {"milestone": "First customer update", "minutes": 30}
            ]
        elif severity == "sev2":
            milestones = [
                {"milestone": "Response team assembled", "minutes": 15},
                {"milestone": "Initial assessment complete", "minutes": 30},
                {"milestone": "Stakeholder notification", "minutes": 60},
                {"milestone": "Status page update (if needed)", "minutes": 60}
            ]
        elif severity == "sev3":
            milestones = [
                {"milestone": "Team assignment", "minutes": 120},
                {"milestone": "Initial triage complete", "minutes": 240},
                {"milestone": "Resolution plan created", "minutes": 480}
            ]
        else:  # sev4
            milestones = [
                {"milestone": "Backlog creation", "minutes": 1440},
                {"milestone": "Priority assessment", "minutes": 2880}
            ]
        
        return {
            "response_time_minutes": rules["response_time"] // 60,
            "milestones": milestones,
            "update_frequency_minutes": self._get_update_frequency(severity)
        }
    def _determine_escalation(self, severity: str, business_impact: str) -> Dict:
        """Determine escalation requirements and triggers."""
        escalation_rules = {
            "sev1": {
                "immediate": ["Incident Commander", "Engineering Manager"],
                "15_minutes": ["VP Engineering", "Customer Success"],
                "30_minutes": ["CTO"],
                "60_minutes": ["CEO", "All C-Suite"],
                "triggers": ["Extended outage", "Revenue impact", "Media attention"]
            },
            "sev2": {
                "immediate": ["Team Lead", "On-call Engineer"],
                "30_minutes": ["Engineering Manager"],
                "120_minutes": ["VP Engineering"],
                "triggers": ["No progress", "Expanding scope", "Customer escalation"]
            },
            "sev3": {
                "immediate": ["Assigned Engineer"],
                "240_minutes": ["Team Lead"],
                "triggers": ["Issue complexity", "Multiple teams needed"]
            },
            "sev4": {
                "immediate": ["Product Owner"],
                "triggers": ["Customer request", "Stakeholder priority"]
            }
        }
        
        return escalation_rules.get(severity, escalation_rules["sev4"])
    def _determine_recipients(self, severity: str) -> List[str]:
        """Determine who should receive notifications."""
        recipients = {
            "sev1": ["on-call", "engineering-leadership", "executives", "customer-success"],
            "sev2": ["on-call", "engineering-leadership", "product-team"],
            "sev3": ["assigned-team", "team-lead"],
            "sev4": ["assigned-engineer"]
        }
        return recipients.get(severity, recipients["sev4"])
    def _determine_channels(self, severity: str) -> List[str]:
        """Determine communication channels to use."""
        channels = {
            "sev1": ["pager", "phone", "slack", "email", "status-page"],
            "sev2": ["pager", "slack", "email"],
            "sev3": ["slack", "email"],
            "sev4": ["ticket-system"]
        }
        return channels.get(severity, channels["sev4"])
    def _get_update_frequency(self, severity: str) -> int:
        """Get recommended update frequency in minutes."""
        frequencies = {"sev1": 15, "sev2": 30, "sev3": 240, "sev4": 0}
        return frequencies.get(severity, 0)
    def _calculate_confidence(self, description: str, affected_users: str, business_impact: str) -> float:
        """Calculate confidence score for the classification."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence with more specific information
        if '%' in affected_users and any(char.isdigit() for char in affected_users):
            confidence += 0.2
        
        if business_impact.lower() in ['critical', 'high', 'medium', 'low']:
            confidence += 0.15
        
        if len(description.split()) > 5:  # Detailed description
            confidence += 0.15
        
        return min(confidence, 1.0)

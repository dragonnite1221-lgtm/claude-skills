# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin1:
    def _load_communication_templates(self) -> Dict[str, Dict]:
        """Load communication templates for each severity level."""
        return {
            "sev1": {
                "subject": "🚨 [SEV1] {service} - {brief_description}",
                "body": """CRITICAL INCIDENT ALERT

Incident Details:
- Start Time: {timestamp}
- Severity: SEV1 - Critical Outage
- Service: {service}
- Impact: {impact_description}
- Current Status: Investigating

Customer Impact:
{customer_impact}

Response Team:
- Incident Commander: TBD (assigning now)
- Primary Responder: {primary_responder}
- SMEs Required: {subject_matter_experts}

Immediate Actions Taken:
{initial_actions}

War Room: {war_room_link}
Status Page: Will be updated within 15 minutes
Next Update: {next_update_time}

This is a customer-impacting incident requiring immediate attention.

{incident_commander_contact}"""
            },
            "sev2": {
                "subject": "⚠️ [SEV2] {service} - {brief_description}",
                "body": """MAJOR INCIDENT NOTIFICATION

Incident Details:
- Start Time: {timestamp}
- Severity: SEV2 - Major Impact
- Service: {service}
- Impact: {impact_description}
- Current Status: Investigating

User Impact:
{customer_impact}

Response Team:
- Primary Responder: {primary_responder}
- Supporting Team: {supporting_teams}
- Incident Commander: {incident_commander}

Initial Assessment:
{initial_assessment}

Next Steps:
{next_steps}

Updates will be provided every 30 minutes.
Status page: {status_page_link}

{contact_information}"""
            },
            "sev3": {
                "subject": "ℹ️ [SEV3] {service} - {brief_description}",
                "body": """MINOR INCIDENT NOTIFICATION

Incident Details:
- Start Time: {timestamp}
- Severity: SEV3 - Minor Impact
- Service: {service}
- Impact: {impact_description}
- Status: {current_status}

Details:
{incident_details}

Assigned Team: {assigned_team}
Estimated Resolution: {eta}

Workaround: {workaround}

This incident has limited customer impact and is being addressed during normal business hours.

{team_contact}"""
            },
            "sev4": {
                "subject": "[SEV4] {service} - {brief_description}",
                "body": """LOW PRIORITY ISSUE

Issue Details:
- Reported: {timestamp}
- Severity: SEV4 - Low Impact
- Component: {service}
- Description: {description}

This issue will be addressed in the normal development cycle.

Assigned to: {assigned_team}
Target Resolution: {target_date}

{standard_contact}"""
            }
        }

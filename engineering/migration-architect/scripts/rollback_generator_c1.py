# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402


class RollbackGeneratorMixin1:
    def _load_communication_templates(self) -> Dict[str, Dict[str, str]]:
        """Load communication templates"""
        return {
            "rollback_start": {
                "technical": {
                    "subject": "ROLLBACK INITIATED: {migration_name}",
                    "body": """Team,

We have initiated rollback for migration: {migration_name}
Rollback ID: {rollback_id}
Start Time: {start_time}
Estimated Duration: {estimated_duration}

Reason: {rollback_reason}

Current Status: Rolling back phase {current_phase}

Next Updates: Every 15 minutes or upon phase completion

Actions Required:
- Monitor system health dashboards
- Stand by for escalation if needed
- Do not make manual changes during rollback

Incident Commander: {incident_commander}
"""
                },
                "business": {
                    "subject": "System Rollback In Progress - {system_name}",
                    "body": """Business Stakeholders,

We are currently performing a planned rollback of the {system_name} migration due to {rollback_reason}.

Impact: {business_impact}
Expected Resolution: {estimated_completion_time}
Affected Services: {affected_services}

We will provide updates every 30 minutes.

Contact: {business_contact}
"""
                },
                "executive": {
                    "subject": "EXEC ALERT: Critical System Rollback - {system_name}",
                    "body": """Executive Team,

A critical rollback is in progress for {system_name}.

Summary:
- Rollback Reason: {rollback_reason}
- Business Impact: {business_impact}
- Expected Resolution: {estimated_completion_time}
- Customer Impact: {customer_impact}

We are following established procedures and will update hourly.

Escalation: {escalation_contact}
"""
                }
            },
            "rollback_complete": {
                "technical": {
                    "subject": "ROLLBACK COMPLETED: {migration_name}",
                    "body": """Team,

Rollback has been successfully completed for migration: {migration_name}

Summary:
- Start Time: {start_time}
- End Time: {end_time}
- Duration: {actual_duration}
- Phases Completed: {completed_phases}

Validation Results:
{validation_results}

System Status: {system_status}

Next Steps:
- Continue monitoring for 24 hours
- Post-rollback review scheduled for {review_date}
- Root cause analysis to begin

All clear to resume normal operations.

Incident Commander: {incident_commander}
"""
                }
            }
        }

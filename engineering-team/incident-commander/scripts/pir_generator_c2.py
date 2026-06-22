# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin2:
    def _load_severity_guidelines(self) -> Dict[str, Dict]:
        """Load severity-specific PIR guidelines."""
        return {
            "sev1": {
                "required_sections": ["executive_summary", "timeline", "rca", "action_items", "lessons_learned"],
                "required_attendees": ["incident_commander", "technical_leads", "engineering_manager", "product_manager"],
                "timeline_requirement": "Complete timeline with 15-minute intervals",
                "rca_methods": ["five_whys", "fishbone", "timeline"],
                "review_deadline_hours": 24,
                "follow_up_weeks": 4
            },
            "sev2": {
                "required_sections": ["summary", "timeline", "rca", "action_items"],
                "required_attendees": ["incident_commander", "technical_leads", "team_lead"],
                "timeline_requirement": "Key milestone timeline",
                "rca_methods": ["five_whys", "timeline"],
                "review_deadline_hours": 72,
                "follow_up_weeks": 2
            },
            "sev3": {
                "required_sections": ["summary", "rca", "action_items"],
                "required_attendees": ["technical_lead", "team_member"],
                "timeline_requirement": "Basic timeline",
                "rca_methods": ["five_whys"],
                "review_deadline_hours": 168,  # 1 week
                "follow_up_weeks": 1
            },
            "sev4": {
                "required_sections": ["summary", "action_items"],
                "required_attendees": ["assigned_engineer"],
                "timeline_requirement": "Optional",
                "rca_methods": ["brief_analysis"],
                "review_deadline_hours": 336,  # 2 weeks
                "follow_up_weeks": 0
            }
        }
    def _load_action_item_types(self) -> Dict[str, Dict]:
        """Load action item categorization and templates."""
        return {
            "immediate_fix": {
                "priority": "P0",
                "timeline": "24-48 hours",
                "description": "Critical bugs or security issues that need immediate attention",
                "template": "Fix {issue_description} to prevent recurrence of {incident_type}",
                "owners": ["engineer", "team_lead"]
            },
            "process_improvement": {
                "priority": "P1",
                "timeline": "1-2 weeks",
                "description": "Process gaps or communication issues identified",
                "template": "Improve {process_area} to address {gap_description}",
                "owners": ["team_lead", "process_owner"]
            },
            "monitoring_alerting": {
                "priority": "P1",
                "timeline": "1 week",
                "description": "Missing monitoring or alerting capabilities",
                "template": "Implement {monitoring_type} for {system_component}",
                "owners": ["sre", "engineer"]
            },
            "documentation": {
                "priority": "P2",
                "timeline": "2-3 weeks", 
                "description": "Documentation gaps or runbook updates",
                "template": "Update {documentation_type} to include {missing_information}",
                "owners": ["technical_writer", "engineer"]
            },
            "training": {
                "priority": "P2",
                "timeline": "1 month",
                "description": "Training needs or knowledge gaps",
                "template": "Provide {training_type} training on {topic}",
                "owners": ["training_coordinator", "subject_matter_expert"]
            },
            "architectural": {
                "priority": "P1-P3",
                "timeline": "1-3 months",
                "description": "System design or architecture improvements",
                "template": "Redesign {system_component} to improve {quality_attribute}",
                "owners": ["architect", "engineering_manager"]
            },
            "tooling": {
                "priority": "P2",
                "timeline": "2-4 weeks",
                "description": "Tool improvements or new tool requirements",
                "template": "Implement {tool_type} to support {use_case}",
                "owners": ["devops", "engineer"]
            }
        }

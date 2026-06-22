# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin10:
    def _map_to_lessons_category(self, category: str) -> str:
        """Map RCA category to lessons learned category."""
        mapping = {
            "people": "team_and_culture",
            "process": "process_and_procedures", 
            "technology": "technical_systems",
            "environment": "technical_systems",
            "unknown": "process_and_procedures"
        }
        return mapping.get(category, "technical_systems")
    def _generate_action_items(self, incident_data: Dict, rca_results: Dict, 
                             lessons_learned: Dict) -> List[Dict]:
        """Generate actionable follow-up items."""
        action_items = []
        
        # Actions from root causes
        root_causes = rca_results.get("root_causes", [])
        for root_cause in root_causes:
            action_type = self._determine_action_type(root_cause)
            action_template = self.action_item_types[action_type]
            
            action_items.append({
                "title": f"Address: {root_cause['cause'][:50]}...",
                "description": root_cause["cause"],
                "type": action_type,
                "priority": action_template["priority"],
                "timeline": action_template["timeline"],
                "owner": "TBD",
                "success_criteria": f"Prevent recurrence of {root_cause['cause'][:30]}...",
                "related_root_cause": root_cause
            })
        
        # Actions from lessons learned
        for category, lessons in lessons_learned.items():
            if len(lessons) > 1:  # Multiple lessons in same category indicate systematic issue
                action_items.append({
                    "title": f"Improve {category.replace('_', ' ')}",
                    "description": f"Address multiple issues identified in {category}",
                    "type": "process_improvement",
                    "priority": "P1",
                    "timeline": "2-3 weeks",
                    "owner": "TBD",
                    "success_criteria": f"Comprehensive review and improvement of {category}"
                })
        
        # Standard actions based on severity
        severity = incident_data.get("severity", "").lower()
        if severity in ["sev1", "critical"]:
            action_items.append({
                "title": "Conduct comprehensive post-incident review",
                "description": "Schedule PIR meeting with all stakeholders",
                "type": "process_improvement",
                "priority": "P0",
                "timeline": "24-48 hours",
                "owner": incident_data.get("incident_commander", "TBD"),
                "success_criteria": "PIR completed and documented"
            })
        
        return action_items
    def _determine_action_type(self, root_cause: Dict) -> str:
        """Determine action item type based on root cause."""
        cause_text = root_cause.get("cause", "").lower()
        category = root_cause.get("category", "").lower()
        
        if any(keyword in cause_text for keyword in ["bug", "error", "failure", "crash"]):
            return "immediate_fix"
        elif any(keyword in cause_text for keyword in ["monitor", "alert", "detect"]):
            return "monitoring_alerting"
        elif any(keyword in cause_text for keyword in ["process", "procedure", "review"]):
            return "process_improvement"
        elif any(keyword in cause_text for keyword in ["document", "runbook", "knowledge"]):
            return "documentation"
        elif any(keyword in cause_text for keyword in ["training", "skill", "knowledge"]):
            return "training"
        elif any(keyword in cause_text for keyword in ["architecture", "design", "system"]):
            return "architectural"
        else:
            return "process_improvement"  # Default
    def _create_timeline_section(self, timeline_data: Optional[Dict], severity: str) -> str:
        """Create timeline section for PIR document."""
        if not timeline_data:
            return "No detailed timeline available."
        
        timeline_content = []
        
        if "timeline" in timeline_data and "phases" in timeline_data["timeline"]:
            timeline_content.append("### Phase Timeline")
            timeline_content.append("")
            
            phases = timeline_data["timeline"]["phases"]
            for phase in phases:
                timeline_content.append(f"**{phase['name'].title()} Phase**")
                timeline_content.append(f"- Start: {phase['start_time']}")
                timeline_content.append(f"- Duration: {phase['duration_minutes']} minutes")
                timeline_content.append(f"- Events: {phase['event_count']}")
                timeline_content.append("")
        
        if "metrics" in timeline_data:
            metrics = timeline_data["metrics"]
            duration_metrics = metrics.get("duration_metrics", {})
            
            timeline_content.append("### Key Metrics")
            timeline_content.append("")
            timeline_content.append(f"- Total Duration: {duration_metrics.get('total_duration_minutes', 'N/A')} minutes")
            timeline_content.append(f"- Time to Mitigation: {duration_metrics.get('time_to_mitigation_minutes', 'N/A')} minutes")
            timeline_content.append(f"- Time to Resolution: {duration_metrics.get('time_to_resolution_minutes', 'N/A')} minutes")
            timeline_content.append("")
        
        return "\n".join(timeline_content)

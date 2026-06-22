# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin12:
    def _create_what_went_well_section(self, incident_info: Dict, rca_results: Dict) -> str:
        """Create what went well section."""
        positives = []
        
        # Generic positive aspects
        if incident_info["status"] == "resolved":
            positives.append("The incident was successfully resolved")
        
        if incident_info["incident_commander"] != "TBD":
            positives.append("Incident command was established")
        
        if len(incident_info.get("responders", [])) > 1:
            positives.append("Multiple team members collaborated on resolution")
        
        # Analysis-specific positives
        if rca_results.get("confidence") == "high":
            positives.append("Root cause analysis provided clear insights")
        
        if not positives:
            positives.append("Incident response process was followed")
        
        return "\n".join([f"- {positive}" for positive in positives])
    def _create_what_went_wrong_section(self, rca_results: Dict, lessons_learned: Dict) -> str:
        """Create what went wrong section."""
        issues = []
        
        # Issues from RCA
        root_causes = rca_results.get("root_causes", [])
        for cause in root_causes[:3]:  # Show top 3
            issues.append(cause["cause"])
        
        # Issues from lessons learned
        for category, lessons in lessons_learned.items():
            if lessons:
                issues.append(f"{category.replace('_', ' ').title()}: {lessons[0]}")
        
        if not issues:
            issues.append("Analysis in progress")
        
        return "\n".join([f"- {issue}" for issue in issues])
    def _create_lessons_learned_section(self, lessons_learned: Dict) -> str:
        """Create lessons learned section."""
        content = []
        
        for category, lessons in lessons_learned.items():
            if lessons:
                content.append(f"### {category.replace('_', ' ').title()}")
                content.append("")
                
                for lesson in lessons:
                    content.append(f"- {lesson}")
                
                content.append("")
        
        if not content:
            content.append("Lessons learned to be documented following detailed analysis.")
        
        return "\n".join(content)
    def _create_action_items_section(self, action_items: List[Dict]) -> str:
        """Create action items section."""
        if not action_items:
            return "Action items to be defined."
        
        content = []
        
        # Group by priority
        priority_groups = defaultdict(list)
        for item in action_items:
            priority_groups[item.get("priority", "P3")].append(item)
        
        for priority in ["P0", "P1", "P2", "P3"]:
            items = priority_groups.get(priority, [])
            if items:
                content.append(f"### {priority} - {self._get_priority_description(priority)}")
                content.append("")
                
                for item in items:
                    content.append(f"**{item['title']}**")
                    content.append(f"- Owner: {item.get('owner', 'TBD')}")
                    content.append(f"- Timeline: {item.get('timeline', 'TBD')}")
                    content.append(f"- Success Criteria: {item.get('success_criteria', 'TBD')}")
                    content.append("")
        
        return "\n".join(content)
    def _get_priority_description(self, priority: str) -> str:
        """Get human-readable priority description."""
        descriptions = {
            "P0": "Critical - Immediate Action Required",
            "P1": "High Priority - Complete Within 1-2 Weeks", 
            "P2": "Medium Priority - Complete Within 1 Month",
            "P3": "Low Priority - Complete When Capacity Allows"
        }
        return descriptions.get(priority, "Unknown Priority")

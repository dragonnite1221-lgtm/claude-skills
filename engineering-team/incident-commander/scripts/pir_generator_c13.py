# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin13:
    def _create_prevention_section(self, rca_results: Dict, action_items: List[Dict]) -> str:
        """Create prevention and follow-up section."""
        content = []
        
        content.append("### Prevention Measures")
        content.append("")
        content.append("Based on the root cause analysis, the following preventive measures have been identified:")
        content.append("")
        
        # Extract prevention-focused action items
        prevention_items = [item for item in action_items if "prevent" in item.get("description", "").lower()]
        
        if prevention_items:
            for item in prevention_items:
                content.append(f"- {item['title']}: {item.get('description', '')}")
        else:
            content.append("- Implement comprehensive testing for similar scenarios")
            content.append("- Improve monitoring and alerting coverage")  
            content.append("- Enhance error handling and resilience patterns")
        
        content.append("")
        content.append("### Follow-up Schedule")
        content.append("")
        content.append("- 1 week: Review action item progress")
        content.append("- 1 month: Evaluate effectiveness of implemented changes")
        content.append("- 3 months: Conduct follow-up assessment and update preventive measures")
        
        return "\n".join(content)
    def _create_appendix_section(self, incident_info: Dict) -> str:
        """Create appendix section."""
        content = []
        
        content.append("### Additional Information")
        content.append("")
        content.append(f"- Incident ID: {incident_info['incident_id']}")
        content.append(f"- Severity Classification: {incident_info['severity']}")
        
        if incident_info.get("affected_services"):
            content.append(f"- Affected Services: {', '.join(incident_info['affected_services'])}")
        
        content.append("")
        content.append("### References")
        content.append("")
        content.append("- Incident tracking ticket: [Link TBD]")
        content.append("- Monitoring dashboards: [Link TBD]")
        content.append("- Communication thread: [Link TBD]")
        
        return "\n".join(content)
    def _generate_metadata(self, incident_info: Dict, rca_results: Dict, action_items: List[Dict]) -> Dict[str, Any]:
        """Generate PIR metadata for tracking and analysis."""
        return {
            "pir_id": f"PIR-{incident_info['incident_id']}",
            "incident_severity": incident_info["severity"],
            "rca_method": rca_results.get("method", "unknown"),
            "rca_confidence": rca_results.get("confidence", "unknown"),
            "total_action_items": len(action_items),
            "critical_action_items": len([item for item in action_items if item.get("priority") == "P0"]),
            "estimated_prevention_timeline": self._estimate_prevention_timeline(action_items),
            "categories_affected": list(set(item.get("type", "unknown") for item in action_items)),
            "review_completeness": self._assess_review_completeness(incident_info, rca_results, action_items)
        }
    def _estimate_prevention_timeline(self, action_items: List[Dict]) -> str:
        """Estimate timeline for implementing all prevention measures."""
        if not action_items:
            return "unknown"
        
        # Find the longest timeline among action items
        max_weeks = 0
        for item in action_items:
            timeline = item.get("timeline", "")
            if "week" in timeline:
                try:
                    weeks = int(re.findall(r'\d+', timeline)[0])
                    max_weeks = max(max_weeks, weeks)
                except (IndexError, ValueError):
                    pass
            elif "month" in timeline:
                try:
                    months = int(re.findall(r'\d+', timeline)[0])
                    max_weeks = max(max_weeks, months * 4)
                except (IndexError, ValueError):
                    pass
        
        if max_weeks == 0:
            return "1-2 weeks"
        elif max_weeks <= 4:
            return f"{max_weeks} weeks"
        else:
            return f"{max_weeks // 4} months"

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin9:
    def _identify_existing_barriers(self, incident_data: Dict, timeline_data: Optional[Dict]) -> List[Dict]:
        """Identify existing preventive/protective barriers."""
        barriers = []
        
        # Look for evidence of existing controls
        if timeline_data and "timeline" in timeline_data:
            events = timeline_data["timeline"].get("events", [])
            
            for event in events:
                message = event.get("message", "").lower()
                if "alert" in message or "monitoring" in message:
                    barriers.append({
                        "barrier": "Monitoring and alerting system",
                        "type": "detective",
                        "effectiveness": "partial"
                    })
                elif "rollback" in message:
                    barriers.append({
                        "barrier": "Rollback capability", 
                        "type": "corrective",
                        "effectiveness": "effective"
                    })
        
        return barriers
    def _recommend_additional_barriers(self, threats: List[Dict], consequences: List[Dict]) -> List[Dict]:
        """Recommend additional barriers based on threats and consequences."""
        recommendations = []
        
        for threat in threats:
            if "deployment" in threat["threat"].lower():
                recommendations.append({
                    "barrier": "Enhanced pre-deployment testing",
                    "type": "preventive",
                    "justification": "Prevent defective deployments reaching production"
                })
            elif "load" in threat["threat"].lower():
                recommendations.append({
                    "barrier": "Auto-scaling and load shedding",
                    "type": "preventive",
                    "justification": "Handle unexpected load increases automatically"
                })
        
        return recommendations
    def _calculate_rca_confidence(self, analysis_data: Any, incident_data: Dict) -> str:
        """Calculate confidence level for RCA results."""
        # Simple heuristic based on available data
        confidence_score = 0
        
        # More detailed incident data increases confidence
        if incident_data.get("description") and len(incident_data["description"]) > 50:
            confidence_score += 1
        
        if incident_data.get("timeline") or incident_data.get("events"):
            confidence_score += 2
        
        if incident_data.get("logs") or incident_data.get("monitoring_data"):
            confidence_score += 2
        
        # Analysis data completeness
        if isinstance(analysis_data, list) and len(analysis_data) > 3:
            confidence_score += 1
        elif isinstance(analysis_data, dict) and len(analysis_data) > 5:
            confidence_score += 1
        
        if confidence_score >= 4:
            return "high"
        elif confidence_score >= 2:
            return "medium"
        else:
            return "low"
    def _generate_lessons_learned(self, incident_data: Dict, timeline_data: Optional[Dict], 
                                rca_results: Dict) -> Dict[str, List[str]]:
        """Generate categorized lessons learned."""
        lessons = defaultdict(list)
        
        # Lessons from RCA
        root_causes = rca_results.get("root_causes", [])
        for root_cause in root_causes:
            category = root_cause.get("category", "technical_systems").lower()
            category_key = self._map_to_lessons_category(category)
            
            lesson = f"Identified: {root_cause['cause']}"
            lessons[category_key].append(lesson)
        
        # Lessons from timeline analysis
        if timeline_data and "gap_analysis" in timeline_data:
            gaps = timeline_data["gap_analysis"].get("gaps", [])
            for gap in gaps:
                if gap.get("severity") == "critical":
                    lessons["response_and_escalation"].append(
                        f"Response time gap: {gap['type'].replace('_', ' ')} took {gap['gap_minutes']} minutes"
                    )
        
        # Generic lessons based on incident characteristics
        severity = incident_data.get("severity", "").lower()
        if severity in ["sev1", "critical"]:
            lessons["detection_and_monitoring"].append(
                "Critical incidents require immediate detection and alerting"
            )
        
        return dict(lessons)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin8:
    def _analyze_response_effectiveness(self, timeline_data: Dict) -> Dict[str, Any]:
        """Analyze the effectiveness of incident response."""
        effectiveness = {
            "overall_rating": "unknown",
            "strengths": [],
            "weaknesses": [],
            "metrics": {}
        }
        
        if "metrics" in timeline_data:
            metrics = timeline_data["metrics"]
            duration_metrics = metrics.get("duration_metrics", {})
            
            # Analyze response times
            time_to_mitigation = duration_metrics.get("time_to_mitigation_minutes", 0)
            time_to_resolution = duration_metrics.get("time_to_resolution_minutes", 0)
            
            if time_to_mitigation <= 30:
                effectiveness["strengths"].append("Quick mitigation response")
            else:
                effectiveness["weaknesses"].append("Slow mitigation response")
            
            if time_to_resolution <= 120:
                effectiveness["strengths"].append("Fast resolution")
            else:
                effectiveness["weaknesses"].append("Extended resolution time")
            
            effectiveness["metrics"] = {
                "time_to_mitigation": time_to_mitigation,
                "time_to_resolution": time_to_resolution
            }
        
        # Overall rating based on strengths vs weaknesses
        if len(effectiveness["strengths"]) > len(effectiveness["weaknesses"]):
            effectiveness["overall_rating"] = "effective"
        elif len(effectiveness["weaknesses"]) > len(effectiveness["strengths"]):
            effectiveness["overall_rating"] = "needs_improvement"
        else:
            effectiveness["overall_rating"] = "mixed"
        
        return effectiveness
    def _extract_timeline_root_causes(self, decision_points: List, missed_opportunities: List, 
                                    response_analysis: Dict) -> List[Dict]:
        """Extract root causes from timeline analysis."""
        root_causes = []
        
        # Root causes from missed opportunities
        for opportunity in missed_opportunities:
            if opportunity["gap_minutes"] > 60:  # Significant gaps
                root_causes.append({
                    "cause": f"Delayed response: {opportunity['opportunity']}",
                    "category": "Process",
                    "evidence": f"{opportunity['gap_minutes']} minute gap identified",
                    "confidence": "high"
                })
        
        # Root causes from response effectiveness
        for weakness in response_analysis.get("weaknesses", []):
            root_causes.append({
                "cause": weakness,
                "category": "Process",
                "evidence": "Timeline analysis",
                "confidence": "medium"
            })
        
        return root_causes
    def _identify_threats(self, incident_data: Dict, timeline_data: Optional[Dict]) -> List[Dict]:
        """Identify threats for Bow Tie analysis."""
        threats = []
        description = incident_data.get("description", "").lower()
        
        if "deployment" in description:
            threats.append({"threat": "Defective code deployment", "likelihood": "medium"})
        if "load" in description or "traffic" in description:
            threats.append({"threat": "Unexpected load increase", "likelihood": "high"})
        if "database" in description:
            threats.append({"threat": "Database performance degradation", "likelihood": "medium"})
        
        return threats
    def _identify_consequences(self, incident_data: Dict) -> List[Dict]:
        """Identify consequences for Bow Tie analysis."""
        consequences = []
        
        customer_impact = incident_data.get("customer_impact", "").lower()
        business_impact = incident_data.get("business_impact", "").lower()
        
        if "all users" in customer_impact or "complete outage" in customer_impact:
            consequences.append({"consequence": "Complete service unavailability", "severity": "critical"})
        
        if "revenue" in business_impact:
            consequences.append({"consequence": "Revenue loss", "severity": "high"})
        
        return consequences

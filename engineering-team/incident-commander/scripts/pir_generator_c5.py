# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin5:
    def _fishbone_analysis(self, incident_data: Dict, timeline_data: Optional[Dict]) -> Dict[str, Any]:
        """Perform Fishbone (Ishikawa) diagram analysis."""
        problem_statement = incident_data.get("description", "Incident occurred")
        
        # Analyze each category
        categories = {}
        for category_info in self.rca_frameworks["fishbone"]["categories"]:
            category_name = category_info["name"]
            contributing_factors = self._identify_category_factors(
                category_name, incident_data, timeline_data
            )
            categories[category_name] = {
                "description": category_info["description"],
                "factors": contributing_factors,
                "examples": category_info["examples"]
            }
        
        # Identify primary contributing factors
        primary_factors = self._identify_primary_factors(categories)
        
        # Generate root cause hypothesis
        root_causes = self._synthesize_fishbone_root_causes(categories, primary_factors)
        
        return {
            "method": "fishbone",
            "problem_statement": problem_statement,
            "categories": categories,
            "primary_factors": primary_factors,
            "root_causes": root_causes,
            "confidence": self._calculate_rca_confidence(categories, incident_data)
        }
    def _timeline_analysis(self, incident_data: Dict, timeline_data: Optional[Dict]) -> Dict[str, Any]:
        """Perform timeline-based root cause analysis."""
        if not timeline_data:
            return {"method": "timeline", "error": "No timeline data provided"}
        
        # Extract key decision points
        decision_points = self._extract_decision_points(timeline_data)
        
        # Identify missed opportunities
        missed_opportunities = self._identify_missed_opportunities(timeline_data)
        
        # Analyze response effectiveness
        response_analysis = self._analyze_response_effectiveness(timeline_data)
        
        # Generate timeline-based root causes
        root_causes = self._extract_timeline_root_causes(
            decision_points, missed_opportunities, response_analysis
        )
        
        return {
            "method": "timeline",
            "decision_points": decision_points,
            "missed_opportunities": missed_opportunities,
            "response_analysis": response_analysis,
            "root_causes": root_causes,
            "confidence": self._calculate_rca_confidence(timeline_data, incident_data)
        }
    def _bow_tie_analysis(self, incident_data: Dict, timeline_data: Optional[Dict]) -> Dict[str, Any]:
        """Perform Bow Tie analysis."""
        # Identify the top event (what went wrong)
        top_event = incident_data.get("description", "Service failure")
        
        # Identify threats (what caused it)
        threats = self._identify_threats(incident_data, timeline_data)
        
        # Identify consequences (impact)
        consequences = self._identify_consequences(incident_data)
        
        # Identify existing barriers
        existing_barriers = self._identify_existing_barriers(incident_data, timeline_data)
        
        # Recommend additional barriers
        recommended_barriers = self._recommend_additional_barriers(threats, consequences)
        
        return {
            "method": "bow_tie",
            "top_event": top_event,
            "threats": threats,
            "consequences": consequences,
            "existing_barriers": existing_barriers,
            "recommended_barriers": recommended_barriers,
            "confidence": self._calculate_rca_confidence(threats, incident_data)
        }

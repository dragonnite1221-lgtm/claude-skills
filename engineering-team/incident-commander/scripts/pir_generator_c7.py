# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin7:
    def _identify_primary_factors(self, categories: Dict) -> List[Dict]:
        """Identify primary contributing factors across all categories."""
        primary_factors = []
        
        for category_name, category_data in categories.items():
            high_likelihood_factors = [
                f for f in category_data["factors"] 
                if f.get("likelihood") == "high"
            ]
            primary_factors.extend([
                {**factor, "category": category_name} 
                for factor in high_likelihood_factors
            ])
        
        return primary_factors
    def _synthesize_fishbone_root_causes(self, categories: Dict, primary_factors: List[Dict]) -> List[Dict]:
        """Synthesize root causes from Fishbone analysis."""
        root_causes = []
        
        # Group primary factors by category
        category_factors = defaultdict(list)
        for factor in primary_factors:
            category_factors[factor["category"]].append(factor)
        
        # Create root causes from categories with multiple factors
        for category, factors in category_factors.items():
            if len(factors) > 1:
                root_causes.append({
                    "cause": f"Multiple {category.lower()} issues contributed to the incident",
                    "category": category,
                    "contributing_factors": [f["factor"] for f in factors],
                    "confidence": "high"
                })
            elif len(factors) == 1:
                root_causes.append({
                    "cause": factors[0]["factor"],
                    "category": category,
                    "confidence": "medium"
                })
        
        return root_causes
    def _has_delayed_response(self, timeline_data: Dict) -> bool:
        """Check if timeline shows delayed response patterns."""
        if not timeline_data or "gap_analysis" not in timeline_data:
            return False
        
        gaps = timeline_data["gap_analysis"].get("gaps", [])
        return any(gap.get("type") == "phase_transition" for gap in gaps)
    def _extract_decision_points(self, timeline_data: Dict) -> List[Dict]:
        """Extract key decision points from timeline."""
        decision_points = []
        
        if "timeline" in timeline_data and "phases" in timeline_data["timeline"]:
            phases = timeline_data["timeline"]["phases"]
            
            for i, phase in enumerate(phases):
                if phase["name"] in ["escalation", "mitigation"]:
                    decision_points.append({
                        "timestamp": phase["start_time"],
                        "decision": f"Initiated {phase['name']} phase",
                        "phase": phase["name"],
                        "duration": phase["duration_minutes"]
                    })
        
        return decision_points
    def _identify_missed_opportunities(self, timeline_data: Dict) -> List[Dict]:
        """Identify missed opportunities from gap analysis."""
        missed_opportunities = []
        
        if "gap_analysis" in timeline_data:
            gaps = timeline_data["gap_analysis"].get("gaps", [])
            
            for gap in gaps:
                if gap.get("severity") == "critical":
                    missed_opportunities.append({
                        "opportunity": f"Earlier {gap['type'].replace('_', ' ')}",
                        "gap_minutes": gap["gap_minutes"],
                        "potential_impact": "Could have reduced incident duration"
                    })
        
        return missed_opportunities

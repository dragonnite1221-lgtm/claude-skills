# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin14:
    def _assess_review_completeness(self, incident_info: Dict, rca_results: Dict, action_items: List[Dict]) -> float:
        """Assess completeness of the PIR (0-1 score)."""
        score = 0.0
        
        # Basic information completeness
        if incident_info.get("description"):
            score += 0.1
        if incident_info.get("start_time"):
            score += 0.1
        if incident_info.get("customer_impact"):
            score += 0.1
        
        # RCA completeness
        if rca_results.get("root_causes"):
            score += 0.2
        if rca_results.get("confidence") in ["medium", "high"]:
            score += 0.1
        
        # Action items completeness
        if action_items:
            score += 0.2
        if any(item.get("owner") and item["owner"] != "TBD" for item in action_items):
            score += 0.1
        
        # Additional factors
        if incident_info.get("incident_commander") != "TBD":
            score += 0.1
        if len(action_items) >= 3:  # Multiple action items show thorough analysis
            score += 0.1
        
        return min(score, 1.0)

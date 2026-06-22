# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin6:
    def _explain_classification(self, severity: str, description: str, affected_users: str) -> str:
        """Provide explanation for the classification decision."""
        rules = self.severity_rules[severity]
        
        matched_keywords = []
        for keyword in rules["keywords"]:
            if keyword in description.lower():
                matched_keywords.append(keyword)
        
        explanation = f"Classified as {severity.upper()} based on: "
        reasons = []
        
        if matched_keywords:
            reasons.append(f"keywords: {', '.join(matched_keywords[:3])}")
        
        if '%' in affected_users:
            reasons.append(f"user impact: {affected_users}")
        
        if not reasons:
            reasons.append("default classification based on available information")
        
        return explanation + "; ".join(reasons)

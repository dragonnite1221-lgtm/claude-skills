# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402
from root_cause_analyzer_p0 import CAPARecommendation, RootCauseFinding  # noqa: F401,E501


class RootCauseAnalyzerMixin1:
    def generate_recommendations(
        self,
        root_causes: List[RootCauseFinding],
        problem: str
    ) -> List[CAPARecommendation]:
        """Generate CAPA recommendations based on root causes."""
        recommendations = []

        for i, cause in enumerate(root_causes, 1):
            # Corrective action (fix the immediate cause)
            recommendations.append(CAPARecommendation(
                action_id=f"CA-{i:03d}",
                action_type="Corrective",
                description=f"Address immediate cause: {cause.description}",
                addresses_cause=cause.cause_id,
                priority=self._assess_priority(cause),
                estimated_effort=self._estimate_effort(cause),
                responsible_role=self._suggest_responsible(cause),
                effectiveness_criteria=[
                    f"Elimination of {cause.description} confirmed by audit",
                    "No recurrence within 90 days",
                    "Metrics return to acceptable range"
                ]
            ))

            # Preventive action (prevent recurrence in other areas)
            if cause.systemic:
                recommendations.append(CAPARecommendation(
                    action_id=f"PA-{i:03d}",
                    action_type="Preventive",
                    description=f"Systemic prevention: Update process/procedure to prevent similar issues",
                    addresses_cause=cause.cause_id,
                    priority="Medium",
                    estimated_effort="2-4 weeks",
                    responsible_role="Quality Manager",
                    effectiveness_criteria=[
                        "Updated procedure approved and implemented",
                        "Training completed for affected personnel",
                        "No similar issues in related processes within 6 months"
                    ]
                ))

        return recommendations
    def _assess_priority(self, cause: RootCauseFinding) -> str:
        if cause.systemic or "safety" in cause.description.lower():
            return "High"
        elif "quality" in cause.description.lower():
            return "Medium"
        return "Low"
    def _estimate_effort(self, cause: RootCauseFinding) -> str:
        if cause.systemic:
            return "4-8 weeks"
        elif len(cause.contributing_factors) > 3:
            return "2-4 weeks"
        return "1-2 weeks"
    def _suggest_responsible(self, cause: RootCauseFinding) -> str:
        category_roles = {
            "Man": "Training Manager",
            "Machine": "Engineering Manager",
            "Material": "Supply Chain Manager",
            "Method": "Process Owner",
            "Measurement": "Quality Engineer",
            "Environment": "Facilities Manager",
            "Management": "Department Head",
            "Software": "IT/Software Manager"
        }
        cat_key = cause.category.split(" (")[0] if "(" in cause.category else cause.category
        return category_roles.get(cat_key, "Quality Manager")

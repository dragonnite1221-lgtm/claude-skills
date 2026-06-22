# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402
from debt_prioritizer_p0 import BusinessImpact  # noqa: F401,E501


class DebtPrioritizerMixin3:
    def _categorize_debt_item(self, item: Dict[str, Any]) -> str:
        """Categorize debt item into high-level categories."""
        debt_type = item.get("type", "unknown")
        
        categories = {
            "code_quality": ["large_function", "high_complexity", "duplicate_code", 
                           "long_line", "missing_docstring"],
            "architecture": ["architecture_debt", "large_file"],
            "security": ["security_risk", "hardcoded_secrets"],
            "testing": ["test_debt", "missing_tests"],
            "maintenance": ["todo_comment", "commented_code"],
            "dependencies": ["dependency_debt", "outdated_packages"],
            "infrastructure": ["deployment_debt", "monitoring_gaps"],
            "documentation": ["missing_docstring", "outdated_docs"]
        }
        
        for category, types in categories.items():
            if debt_type in types:
                return category
        
        return "other"
    def _generate_impact_tags(self, item: Dict[str, Any], 
                            business_impact: BusinessImpact) -> List[str]:
        """Generate impact tags for debt item."""
        tags = []
        
        if business_impact.security_impact >= 7:
            tags.append("security-critical")
        if business_impact.customer_impact >= 7:
            tags.append("customer-facing")
        if business_impact.revenue_impact >= 7:
            tags.append("revenue-impact")
        if business_impact.team_velocity_impact >= 7:
            tags.append("velocity-blocker")
        if business_impact.quality_impact >= 7:
            tags.append("quality-risk")
        
        # Add effort-based tags
        effort_hours = item.get("effort_estimate", {}).get("hours_estimate", 0)
        if effort_hours <= 4:
            tags.append("quick-win")
        elif effort_hours >= 40:
            tags.append("major-initiative")
        
        return tags
    def _calculate_cost_of_delay_score(self, item: Dict[str, Any]) -> float:
        """Calculate priority score using cost-of-delay framework."""
        business_impact = item["business_impact"]
        effort = item["effort_estimate"]
        
        # Business value (weighted average of impacts)
        business_value = (
            business_impact["customer_impact"] * 0.3 +
            business_impact["revenue_impact"] * 0.3 +
            business_impact["quality_impact"] * 0.2 +
            business_impact["team_velocity_impact"] * 0.2
        )
        
        # Urgency (how quickly value decreases)
        urgency = item["interest_rate"]["daily_cost"] * 10  # Scale to 1-10
        urgency = min(10, max(1, urgency))
        
        # Risk reduction
        risk_reduction = business_impact["security_impact"] * 0.6 + business_impact["quality_impact"] * 0.4
        
        # Team productivity impact
        team_productivity = business_impact["team_velocity_impact"]
        
        # Combine with weights
        weights = self.framework_weights["cost_of_delay"]
        numerator = (
            business_value * weights["business_value"] +
            urgency * weights["urgency"] +
            risk_reduction * weights["risk_reduction"] +
            team_productivity * weights["team_productivity"]
        )
        
        # Divide by effort (adjusted for risk)
        effort_adjusted = effort["hours_estimate"] * effort["risk_factor"]
        denominator = max(1, effort_adjusted / 8)  # Normalize to story points
        
        return round(numerator / denominator, 2)

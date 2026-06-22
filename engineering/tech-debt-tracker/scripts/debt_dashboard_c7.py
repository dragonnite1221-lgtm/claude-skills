# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin7:
    def _generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for debt management."""
        recommendations = []
        
        if not self.health_history:
            return recommendations
        
        current_health = self.health_history[-1]
        current_snapshot = self.processed_snapshots[-1] if self.processed_snapshots else {}
        
        # Health-based recommendations
        if current_health["overall_score"] < 50:
            recommendations.append({
                "priority": "critical",
                "category": "immediate_action",
                "title": "Initiate Emergency Debt Reduction",
                "description": "Current health score is critically low. Consider dedicating 50%+ of development capacity to debt reduction.",
                "impact": "high",
                "effort": "high"
            })
        
        # Velocity impact recommendations
        if current_health["velocity_impact"] > 25:
            recommendations.append({
                "priority": "high",
                "category": "productivity",
                "title": "Address Velocity Blockers",
                "description": f"Technical debt is reducing team velocity by {current_health['velocity_impact']:.1f}%. Focus on high-impact debt items first.",
                "impact": "high",
                "effort": "medium"
            })
        
        # Security recommendations
        if current_health["technical_risk_score"] > 70:
            recommendations.append({
                "priority": "high",
                "category": "security",
                "title": "Security Debt Review Required",
                "description": "High technical risk score indicates security vulnerabilities. Conduct immediate security debt audit.",
                "impact": "high",
                "effort": "medium"
            })
        
        # Trend-based recommendations
        health_trend = self.trend_analyses.get("overall_score")
        if health_trend and health_trend.trend_direction == "declining":
            recommendations.append({
                "priority": "medium",
                "category": "process",
                "title": "Implement Debt Prevention Measures",
                "description": "Health score is declining over time. Establish coding standards, automated quality gates, and regular debt reviews.",
                "impact": "medium",
                "effort": "medium"
            })
        
        # Category-specific recommendations
        if current_snapshot:
            debt_by_category = current_snapshot["debt_by_category"]
            top_category = debt_by_category.most_common(1)[0] if debt_by_category else None
            
            if top_category and top_category[1] > 10:
                category, count = top_category
                recommendations.append({
                    "priority": "medium",
                    "category": "focus_area",
                    "title": f"Focus on {category.replace('_', ' ').title()} Debt",
                    "description": f"{category.replace('_', ' ').title()} represents the largest debt category ({count} items). Consider targeted initiatives.",
                    "impact": "medium",
                    "effort": "medium"
                })
        
        # Velocity-based recommendations
        if self.velocity_history:
            recent_velocities = self.velocity_history[-3:] if len(self.velocity_history) >= 3 else self.velocity_history
            avg_velocity_ratio = mean([v.velocity_ratio for v in recent_velocities])
            
            if avg_velocity_ratio < 0.8:
                recommendations.append({
                    "priority": "medium",
                    "category": "capacity",
                    "title": "Increase Debt Resolution Capacity",
                    "description": "Debt is accumulating faster than resolution. Consider increasing debt budget or improving resolution efficiency.",
                    "impact": "medium",
                    "effort": "low"
                })
        
        return recommendations

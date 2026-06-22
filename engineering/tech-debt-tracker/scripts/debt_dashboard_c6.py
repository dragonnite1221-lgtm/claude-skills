# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin6:
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of debt status."""
        if not self.health_history:
            return {}
        
        current_health = self.health_history[-1]
        
        # Determine overall status
        score = current_health["overall_score"]
        if score >= self.thresholds["excellent"]:
            status = "excellent"
            status_message = "Code quality is excellent with minimal technical debt."
        elif score >= self.thresholds["good"]:
            status = "good" 
            status_message = "Code quality is good with manageable technical debt."
        elif score >= self.thresholds["fair"]:
            status = "fair"
            status_message = "Code quality needs attention. Technical debt is accumulating."
        else:
            status = "poor"
            status_message = "Critical: High levels of technical debt requiring immediate action."
        
        # Key insights
        insights = []
        
        if len(self.health_history) > 1:
            prev_health = self.health_history[-2]
            score_change = current_health["overall_score"] - prev_health["overall_score"]
            
            if score_change > 5:
                insights.append("Health score improving significantly")
            elif score_change < -5:
                insights.append("Health score declining - attention needed")
        
        if current_health["velocity_impact"] > 20:
            insights.append("High velocity impact detected - development speed affected")
        
        if current_health["technical_risk_score"] > 70:
            insights.append("High technical risk - security and stability concerns")
        
        # Debt velocity insight
        if self.velocity_history:
            recent_velocity = self.velocity_history[-1]
            if recent_velocity.velocity_ratio < 0.5:
                insights.append("Debt accumulating faster than resolution")
            elif recent_velocity.velocity_ratio > 1.5:
                insights.append("Good progress on debt reduction")
        
        return {
            "overall_status": status,
            "health_score": current_health["overall_score"],
            "status_message": status_message,
            "key_insights": insights,
            "total_debt_items": self.processed_snapshots[-1]["total_debt_items"] if self.processed_snapshots else 0,
            "estimated_effort_hours": self.processed_snapshots[-1]["total_effort_estimate"] if self.processed_snapshots else 0,
            "high_priority_items": self.processed_snapshots[-1]["high_priority_count"] if self.processed_snapshots else 0,
            "velocity_impact_percent": current_health["velocity_impact"]
        }

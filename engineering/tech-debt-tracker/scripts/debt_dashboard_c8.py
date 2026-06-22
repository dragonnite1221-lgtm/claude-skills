# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin8:
    def _generate_visualization_data(self) -> Dict[str, Any]:
        """Generate data for dashboard visualizations."""
        visualizations = {}
        
        # Health score timeline
        visualizations["health_timeline"] = [
            {
                "date": entry["date"][:10],  # Date only
                "overall_score": entry["overall_score"],
                "quality_score": entry["quality_score"],
                "technical_risk": entry["technical_risk_score"]
            }
            for entry in self.health_history
        ]
        
        # Debt accumulation trend
        visualizations["debt_accumulation"] = [
            {
                "date": snapshot["date"][:10],
                "total_debt": snapshot["total_debt_items"],
                "high_priority": snapshot["high_priority_count"],
                "security_debt": snapshot["security_debt_count"]
            }
            for snapshot in self.processed_snapshots
        ]
        
        # Category distribution (latest snapshot)
        if self.processed_snapshots:
            latest_categories = self.processed_snapshots[-1]["debt_by_category"]
            visualizations["category_distribution"] = [
                {"category": category, "count": count}
                for category, count in latest_categories.items()
            ]
        
        # Velocity chart
        visualizations["debt_velocity"] = [
            {
                "period": velocity.period,
                "new_items": velocity.new_debt_items,
                "resolved_items": velocity.resolved_debt_items,
                "net_change": velocity.net_change,
                "velocity_ratio": velocity.velocity_ratio
            }
            for velocity in self.velocity_history
        ]
        
        # Effort estimation trend
        visualizations["effort_trend"] = [
            {
                "date": snapshot["date"][:10],
                "total_effort": snapshot["total_effort_estimate"]
            }
            for snapshot in self.processed_snapshots
        ]
        
        return visualizations
    def _get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics for the current state."""
        if not self.processed_snapshots:
            return {}
        
        current = self.processed_snapshots[-1]
        
        return {
            "debt_breakdown": dict(current["debt_by_type"]),
            "severity_breakdown": dict(current["debt_by_severity"]),
            "category_breakdown": dict(current["debt_by_category"]),
            "files_analyzed": current["total_files"],
            "debt_density": current["total_debt_items"] / max(1, current["total_files"]),
            "average_effort_per_item": current["total_effort_estimate"] / max(1, current["total_debt_items"])
        }

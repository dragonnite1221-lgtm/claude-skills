# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402
from debt_dashboard_p0 import DebtVelocity  # noqa: F401,E501


class DebtDashboardMixin5:
    def _calculate_debt_velocity(self, period: str):
        """Calculate debt velocity between snapshots."""
        self.velocity_history = []
        
        if len(self.processed_snapshots) < 2:
            return
        
        for i in range(1, len(self.processed_snapshots)):
            current = self.processed_snapshots[i]
            previous = self.processed_snapshots[i-1]
            
            # Track debt by unique identifiers when possible
            current_debt_ids = set()
            previous_debt_ids = set()
            
            current_effort = current["total_effort_estimate"]
            previous_effort = previous["total_effort_estimate"]
            
            # Simple approach: compare total counts and effort
            debt_change = current["total_debt_items"] - previous["total_debt_items"]
            effort_change = current_effort - previous_effort
            
            # Estimate new vs resolved (rough approximation)
            if debt_change >= 0:
                new_debt_items = debt_change
                resolved_debt_items = 0
            else:
                new_debt_items = 0
                resolved_debt_items = abs(debt_change)
            
            # Calculate velocity ratio
            if new_debt_items > 0:
                velocity_ratio = resolved_debt_items / new_debt_items
            else:
                velocity_ratio = float('inf') if resolved_debt_items > 0 else 1.0
            
            velocity = DebtVelocity(
                period=f"{previous['date'][:10]} to {current['date'][:10]}",
                new_debt_items=new_debt_items,
                resolved_debt_items=resolved_debt_items,
                net_change=debt_change,
                velocity_ratio=min(10.0, velocity_ratio),  # Cap at 10 for display
                effort_hours_added=max(0, effort_change),
                effort_hours_resolved=max(0, -effort_change),
                net_effort_change=effort_change
            )
            
            self.velocity_history.append(velocity)
    def _generate_forecasts(self) -> Dict[str, Any]:
        """Generate forecasts based on trend analysis."""
        if not self.trend_analyses:
            return {}
        
        forecasts = {}
        
        # Overall health forecast
        health_trend = self.trend_analyses.get("overall_score")
        if health_trend:
            current_score = self.health_history[-1]["overall_score"]
            forecasts["health_score_3_months"] = max(0, min(100, 
                current_score + (health_trend.change_rate * 3)))
            forecasts["health_score_6_months"] = max(0, min(100,
                current_score + (health_trend.change_rate * 6)))
        
        # Debt accumulation forecast
        if self.velocity_history:
            avg_net_change = mean([v.net_change for v in self.velocity_history[-3:]])  # Last 3 periods
            current_debt = self.processed_snapshots[-1]["total_debt_items"]
            
            forecasts["debt_count_3_months"] = max(0, current_debt + (avg_net_change * 3))
            forecasts["debt_count_6_months"] = max(0, current_debt + (avg_net_change * 6))
        
        # Risk forecast
        risk_trend = self.trend_analyses.get("technical_risk_score")
        if risk_trend:
            current_risk = self.health_history[-1]["technical_risk_score"]
            forecasts["risk_score_3_months"] = max(0, min(100,
                current_risk + (risk_trend.change_rate * 3)))
        
        return forecasts

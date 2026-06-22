# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402
from debt_prioritizer_p0 import BusinessImpact, EffortEstimate, InterestRate  # noqa: F401,E501


class DebtPrioritizerMixin2:
    def _assess_business_impact(self, item: Dict[str, Any]) -> BusinessImpact:
        """Assess business impact of debt item."""
        debt_type = item.get("type", "unknown")
        severity = item.get("severity", "medium")
        
        # Base impact scores by debt type (1-10 scale)
        impact_profiles = {
            "security_risk": (9, 8, 7, 9, 10),  # customer, revenue, velocity, quality, security
            "architecture_debt": (6, 7, 9, 8, 4),
            "large_function": (3, 4, 7, 6, 2),
            "high_complexity": (4, 5, 8, 7, 3),
            "duplicate_code": (3, 4, 6, 6, 2),
            "syntax_error": (7, 6, 8, 9, 3),
            "test_debt": (5, 5, 7, 8, 3),
            "dependency_debt": (6, 5, 6, 7, 7),
            "todo_comment": (1, 1, 2, 2, 1),
            "missing_docstring": (2, 2, 4, 3, 1)
        }
        
        base_impacts = impact_profiles.get(debt_type, (3, 3, 5, 5, 3))
        
        # Adjust by severity
        severity_adjustments = {
            "low": 0.6,
            "medium": 1.0,
            "high": 1.4,
            "critical": 1.8
        }
        
        adjustment = severity_adjustments.get(severity, 1.0)
        
        # Apply adjustment and cap at 10
        adjusted_impacts = [min(10, max(1, round(impact * adjustment))) 
                          for impact in base_impacts]
        
        return BusinessImpact(
            customer_impact=adjusted_impacts[0],
            revenue_impact=adjusted_impacts[1],
            team_velocity_impact=adjusted_impacts[2],
            quality_impact=adjusted_impacts[3],
            security_impact=adjusted_impacts[4]
        )
    def _calculate_interest_rate(self, item: Dict[str, Any], 
                               business_impact: BusinessImpact) -> InterestRate:
        """Calculate interest rate for technical debt."""
        
        # Base daily cost calculation
        velocity_impact = business_impact.team_velocity_impact
        quality_impact = business_impact.quality_impact
        
        # Daily cost in "developer hours lost"
        daily_cost = (velocity_impact * 0.5) + (quality_impact * 0.3)
        
        # Frequency multiplier based on code location and type
        file_path = item.get("file_path", "")
        debt_type = item.get("type", "unknown")
        
        # Estimate frequency based on file path patterns
        frequency_multiplier = 1.0
        if any(pattern in file_path.lower() for pattern in ["main", "core", "auth", "api"]):
            frequency_multiplier = 2.0
        elif any(pattern in file_path.lower() for pattern in ["util", "helper", "common"]):
            frequency_multiplier = 1.5
        elif any(pattern in file_path.lower() for pattern in ["test", "spec", "config"]):
            frequency_multiplier = 0.5
        
        # Team impact multiplier
        team_impact_multiplier = min(self.team_size, 8) / 5.0  # Normalize around team of 5
        
        # Compound rate - how this debt creates more debt
        compound_rates = {
            "architecture_debt": 0.1,  # Creates 10% more debt monthly
            "duplicate_code": 0.08,
            "high_complexity": 0.05,
            "large_function": 0.03,
            "test_debt": 0.04,
            "security_risk": 0.02,  # Doesn't compound much, but high initial impact
            "todo_comment": 0.01
        }
        
        compound_rate = compound_rates.get(debt_type, 0.02)
        
        return InterestRate(
            daily_cost=daily_cost,
            frequency_multiplier=frequency_multiplier,
            team_impact_multiplier=team_impact_multiplier,
            compound_rate=compound_rate
        )
    def _calculate_cost_of_delay(self, interest_rate: InterestRate, 
                               effort: EffortEstimate) -> float:
        """Calculate total cost of delay if debt is not fixed."""
        
        # Estimate delay in days (assuming debt gets fixed eventually)
        estimated_delay_days = effort.hours_estimate / (self.sprint_capacity_hours / 14)  # 2-week sprints
        
        # Calculate cumulative cost
        daily_cost = (interest_rate.daily_cost * 
                     interest_rate.frequency_multiplier * 
                     interest_rate.team_impact_multiplier)
        
        # Add compound interest effect
        compound_effect = (1 + interest_rate.compound_rate) ** (estimated_delay_days / 30)
        
        total_cost = daily_cost * estimated_delay_days * compound_effect
        
        return round(total_cost, 2)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402


@dataclass
class EffortEstimate:
    """Represents effort estimation for a debt item."""
    size_points: int
    hours_estimate: float
    risk_factor: float  # 1.0 = low risk, 1.5 = medium, 2.0+ = high
    skill_level_required: str  # junior, mid, senior, expert
    confidence: float  # 0.0-1.0


@dataclass
class BusinessImpact:
    """Represents business impact assessment for a debt item."""
    customer_impact: int  # 1-10 scale
    revenue_impact: int  # 1-10 scale  
    team_velocity_impact: int  # 1-10 scale
    quality_impact: int  # 1-10 scale
    security_impact: int  # 1-10 scale


@dataclass
class InterestRate:
    """Represents the interest rate calculation for technical debt."""
    daily_cost: float  # cost per day if left unfixed
    frequency_multiplier: float  # how often this code is touched
    team_impact_multiplier: float  # how many developers affected
    compound_rate: float  # how quickly this debt makes other debt worse


def format_prioritized_report(analysis_result: Dict[str, Any]) -> str:
    """Format the prioritization analysis in human-readable format."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("TECHNICAL DEBT PRIORITIZATION REPORT")
    output.append("=" * 60)
    metadata = analysis_result["metadata"]
    output.append(f"Analysis Date: {metadata['analysis_date']}")
    output.append(f"Framework: {metadata['framework_used'].upper()}")
    output.append(f"Team Size: {metadata['team_size']}")
    output.append(f"Sprint Capacity: {metadata['sprint_capacity_hours']} hours")
    output.append("")
    
    # Executive Summary
    insights = analysis_result["insights"]
    output.append("EXECUTIVE SUMMARY")
    output.append("-" * 30)
    output.append(f"Total Debt Items: {metadata['total_items_analyzed']}")
    output.append(f"Total Effort Required: {insights['total_effort_hours']} hours")
    output.append(f"Total Cost of Delay: ${insights['total_cost_of_delay']:,.0f}")
    output.append(f"Quick Wins Available: {insights['quick_wins_count']}")
    output.append(f"High-Risk Items: {insights['high_risk_items_count']}")
    output.append("")
    
    # Sprint Plan
    sprint_plan = analysis_result["sprint_allocation"]
    output.append("SPRINT ALLOCATION PLAN")
    output.append("-" * 30)
    output.append(f"Sprints Needed: {sprint_plan['total_sprints_needed']}")
    output.append(f"Hours per Sprint: {sprint_plan['debt_capacity_per_sprint']}")
    output.append("")
    
    for sprint in sprint_plan["sprint_plan"][:3]:  # Show first 3 sprints
        output.append(f"Sprint {sprint['sprint_number']} ({sprint['capacity_used']:.0%} capacity):")
        for item in sprint["items"][:3]:  # Top 3 items per sprint
            output.append(f"  • {item['description'][:50]}...")
            output.append(f"    Effort: {item['effort_estimate']['hours_estimate']:.1f}h, "
                        f"Priority: {item['priority_score']}")
        output.append("")
    
    # Top Priority Items
    output.append("TOP 10 PRIORITY ITEMS")
    output.append("-" * 30)
    for i, item in enumerate(analysis_result["prioritized_backlog"][:10], 1):
        output.append(f"{i}. [{item['priority_score']:.1f}] {item['description']}")
        output.append(f"   Category: {item['category']}, "
                    f"Effort: {item['effort_estimate']['hours_estimate']:.1f}h, "
                    f"Cost of Delay: ${item['cost_of_delay']:.0f}")
        if item["impact_tags"]:
            output.append(f"   Tags: {', '.join(item['impact_tags'])}")
        output.append("")
    
    # Recommendations
    output.append("RECOMMENDATIONS")
    output.append("-" * 30)
    for i, rec in enumerate(analysis_result["recommendations"], 1):
        output.append(f"{i}. {rec}")
        output.append("")
    
    return "\n".join(output)

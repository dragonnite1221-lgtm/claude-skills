# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p2 import CapacityAnalysisResult  # noqa: E402,E501
# fmt: on


def format_text_output(result: CapacityAnalysisResult) -> str:
    """Format analysis results as readable text report."""
    lines = []
    lines.append("="*60)
    lines.append("RESOURCE CAPACITY PLANNING REPORT")
    lines.append("="*60)
    lines.append("")
    
    if "error" in result.summary:
        lines.append(f"ERROR: {result.summary['error']}")
        return "\n".join(lines)
    
    # Executive Summary
    summary = result.summary
    lines.append("CAPACITY OVERVIEW")
    lines.append("-"*30)
    lines.append(f"Total Resources: {summary['total_resources']}")
    lines.append(f"Total Projects: {summary['total_projects']} ({summary['active_projects']} active)")
    lines.append(f"Capacity vs Demand: {summary['total_capacity_hours']:.0f}h vs {summary['total_demand_hours']:.0f}h per week")
    lines.append(f"Overall Utilization: {summary['overall_utilization']:.1%}")
    lines.append("")
    
    # Resource Utilization
    resource_analysis = result.resource_analysis
    lines.append("RESOURCE UTILIZATION ANALYSIS")
    lines.append("-"*30)
    
    utilization_categories = resource_analysis.get("utilization_categories", {})
    for category, resources in utilization_categories.items():
        if resources:
            lines.append(f"{category.replace('_', ' ').title()}: {len(resources)} resources")
            for resource in resources[:3]:  # Show top 3
                lines.append(f"  - {resource['name']} ({resource['role']}): {resource['utilization']:.1%}")
            if len(resources) > 3:
                lines.append(f"  ... and {len(resources) - 3} more")
    lines.append("")
    
    # Capacity Alerts
    alerts = resource_analysis.get("capacity_alerts", [])
    if alerts:
        lines.append("CAPACITY ALERTS")
        lines.append("-"*30)
        for alert in alerts:
            lines.append(f"⚠️  {alert}")
        lines.append("")
    
    # Project Capacity Gaps
    project_analysis = result.project_analysis
    capacity_gaps = project_analysis.get("capacity_gaps", {})
    
    lines.append("PROJECT CAPACITY GAPS")
    lines.append("-"*30)
    lines.append(f"Projects with gaps: {capacity_gaps.get('projects_with_gaps', 0)}")
    lines.append(f"Total gap: {capacity_gaps.get('total_gap_hours_weekly', 0):.0f} hours/week")
    
    gap_projects = capacity_gaps.get("gap_projects", [])
    if gap_projects:
        lines.append("Top projects needing resources:")
        for project in gap_projects[:5]:
            lines.append(f"  - {project['name']} ({project['priority']}): {project['gap_hours']:.0f}h/week gap")
    lines.append("")
    
    # Skill Demand
    skill_demand = project_analysis.get("skill_demand", {})
    if skill_demand:
        lines.append("TOP SKILL DEMANDS")
        lines.append("-"*30)
        for skill, hours in list(skill_demand.items())[:5]:
            lines.append(f"{skill}: {hours} hours needed")
        lines.append("")
    
    # Optimization Suggestions
    optimization = result.allocation_optimization
    suggested_reallocations = optimization.get("suggested_reallocations", [])
    
    if suggested_reallocations:
        lines.append("RESOURCE REALLOCATION SUGGESTIONS")
        lines.append("-"*30)
        for suggestion in suggested_reallocations[:3]:
            lines.append(f"Project: {suggestion['project_name']}")
            lines.append(f"  Gap: {suggestion['gap_hours']:.0f} hours/week")
            recommended = suggestion.get("recommended_resources", [])
            if recommended:
                best_match = recommended[0]
                resource_info = best_match["resource"]
                lines.append(f"  Best fit: {resource_info.name} ({resource_info.role})")
                lines.append(f"  Skill match: {best_match['skill_match_score']:.1%}")
                lines.append(f"  Available: {best_match['available_hours']:.0f}h/week")
        lines.append("")
    
    # Scenario Analysis
    scenario_analysis = result.scenario_analysis
    if scenario_analysis:
        lines.append("SCENARIO ANALYSIS")
        lines.append("-"*30)
        for scenario_name, results in scenario_analysis.items():
            lines.append(f"{scenario_name}:")
            lines.append(f"  Utilization: {results['resource_utilization']:.1%}")
            lines.append(f"  Capacity gaps: {results['capacity_gaps']:.0f}h/week")
            lines.append(f"  Cost impact: ${results['cost_impact']:.0f}/week")
        lines.append("")
    
    # Recommendations
    if result.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-"*30)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
    
    return "\n".join(lines)

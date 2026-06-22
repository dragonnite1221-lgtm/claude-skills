# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p2 import Project, Resource  # noqa: E402,E501
from resource_capacity_planner_p3 import analyze_resource_utilization  # noqa: E402,E501
from resource_capacity_planner_p4 import analyze_project_capacity_requirements  # noqa: E402,E501
from resource_capacity_planner_p5 import _calculate_cost_impact  # noqa: E402,E501
# fmt: on


def simulate_capacity_scenarios(resources: List[Resource], projects: List[Project], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Simulate what-if scenarios for capacity planning."""
    scenario_results = {}
    
    for scenario in scenarios:
        scenario_name = scenario.get("name", "Unnamed Scenario")
        scenario_type = scenario.get("type", "")
        scenario_params = scenario.get("parameters", {})
        
        # Create copies for simulation
        sim_resources = [Resource(r.__dict__.copy()) for r in resources]
        sim_projects = [Project(p.__dict__.copy()) for p in projects]
        
        # Apply scenario changes
        if scenario_type == "add_resource":
            # Add new resource
            new_resource_data = scenario_params.get("resource_data", {})
            new_resource = Resource(new_resource_data)
            sim_resources.append(new_resource)
            
        elif scenario_type == "remove_resource":
            # Remove resource
            resource_id = scenario_params.get("resource_id", "")
            sim_resources = [r for r in sim_resources if r.id != resource_id]
            
        elif scenario_type == "add_project":
            # Add new project
            new_project_data = scenario_params.get("project_data", {})
            new_project = Project(new_project_data)
            sim_projects.append(new_project)
            
        elif scenario_type == "adjust_utilization":
            # Adjust resource utilization
            resource_id = scenario_params.get("resource_id", "")
            new_utilization = scenario_params.get("new_utilization", 0)
            
            for resource in sim_resources:
                if resource.id == resource_id:
                    resource.current_utilization = new_utilization
                    resource._calculate_effective_capacity()
        
        # Analyze scenario results
        resource_analysis = analyze_resource_utilization(sim_resources)
        project_analysis = analyze_project_capacity_requirements(sim_projects)
        
        scenario_results[scenario_name] = {
            "scenario_type": scenario_type,
            "resource_utilization": resource_analysis["utilization_stats"]["overall_utilization"],
            "total_capacity": resource_analysis["utilization_stats"]["total_capacity"],
            "capacity_gaps": project_analysis["capacity_gaps"]["total_gap_hours_weekly"],
            "under_utilized_count": len(resource_analysis["utilization_categories"]["under_utilized"]),
            "over_utilized_count": len(resource_analysis["utilization_categories"]["over_utilized"]),
            "cost_impact": _calculate_cost_impact(sim_resources, resources)
        }
    
    return scenario_results
def generate_capacity_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
    """Generate actionable capacity management recommendations."""
    recommendations = []
    
    # Resource utilization recommendations
    resource_analysis = analysis_results.get("resource_analysis", {})
    utilization_categories = resource_analysis.get("utilization_categories", {})
    
    critical_count = len(utilization_categories.get("critical", []))
    over_utilized_count = len(utilization_categories.get("over_utilized", []))
    under_utilized_count = len(utilization_categories.get("under_utilized", []))
    
    if critical_count > 0:
        recommendations.append(f"URGENT: Redistribute workload for {critical_count} critically over-allocated resources to prevent burnout.")
    
    if over_utilized_count > 2:
        recommendations.append(f"Consider hiring or redistributing work - {over_utilized_count} team members are over-allocated.")
    
    if under_utilized_count > 0 and critical_count + over_utilized_count > 0:
        recommendations.append(f"Rebalance allocation - {under_utilized_count} under-utilized resources could help with over-allocated work.")
    
    # Project capacity recommendations
    project_analysis = analysis_results.get("project_analysis", {})
    capacity_gaps = project_analysis.get("capacity_gaps", {})
    
    total_gap = capacity_gaps.get("total_gap_hours_weekly", 0)
    if total_gap > 40:  # More than 1 FTE worth of gap
        recommendations.append(f"Capacity shortfall of {total_gap:.0f} hours/week detected. Consider hiring or timeline adjustments.")
    
    # Skill-based recommendations
    skill_demand = project_analysis.get("skill_demand", {})
    if skill_demand:
        top_skill = list(skill_demand.keys())[0]
        top_demand = skill_demand[top_skill]
        recommendations.append(f"High demand for {top_skill} skills ({top_demand} hours). Consider training or specialized hiring.")
    
    # Optimization recommendations
    optimization = analysis_results.get("allocation_optimization", {})
    efficiency = optimization.get("current_allocation_efficiency", 0)
    
    if efficiency < 0.7:
        recommendations.append("Low allocation efficiency detected. Review skill-to-project matching and consider reallocation.")
    
    return recommendations

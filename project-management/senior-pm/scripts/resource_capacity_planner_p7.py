# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p2 import CapacityAnalysisResult, Project, Resource  # noqa: E402,E501
from resource_capacity_planner_p3 import analyze_resource_utilization  # noqa: E402,E501
from resource_capacity_planner_p4 import analyze_project_capacity_requirements  # noqa: E402,E501
from resource_capacity_planner_p5 import optimize_resource_allocation  # noqa: E402,E501
from resource_capacity_planner_p6 import generate_capacity_recommendations, simulate_capacity_scenarios  # noqa: E402,E501
# fmt: on


def analyze_capacity(data: Dict[str, Any]) -> CapacityAnalysisResult:
    """Perform comprehensive capacity analysis."""
    result = CapacityAnalysisResult()
    
    try:
        # Parse resource and project data
        resource_records = data.get("resources", [])
        project_records = data.get("projects", [])
        
        resources = [Resource(record) for record in resource_records]
        projects = [Project(record) for record in project_records]
        
        if not resources:
            raise ValueError("No resource data found")
        
        # Basic summary
        result.summary = {
            "total_resources": len(resources),
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.status in ["active", "in_progress"]]),
            "total_capacity_hours": sum(r.effective_hours_per_week for r in resources),
            "total_demand_hours": sum(p.required_hours_per_week for p in projects if p.status != "completed"),
            "overall_utilization": sum(r.current_utilization for r in resources) / max(len(resources), 1)
        }
        
        # Resource analysis
        result.resource_analysis = analyze_resource_utilization(resources)
        
        # Project analysis
        result.project_analysis = analyze_project_capacity_requirements(projects)
        
        # Allocation optimization
        result.allocation_optimization = optimize_resource_allocation(resources, projects)
        
        # Scenario analysis (if scenarios provided)
        scenarios = data.get("scenarios", [])
        if scenarios:
            result.scenario_analysis = simulate_capacity_scenarios(resources, projects, scenarios)
        
        # Generate recommendations
        analysis_data = {
            "resource_analysis": result.resource_analysis,
            "project_analysis": result.project_analysis,
            "allocation_optimization": result.allocation_optimization
        }
        result.recommendations = generate_capacity_recommendations(analysis_data)
        
    except Exception as e:
        result.summary = {"error": str(e)}
    
    return result

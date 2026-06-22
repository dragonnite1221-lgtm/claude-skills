# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p1 import UTILIZATION_THRESHOLDS  # noqa: E402,E501
from resource_capacity_planner_p2 import Project, Resource  # noqa: E402,E501
# fmt: on


def optimize_resource_allocation(resources: List[Resource], projects: List[Project]) -> Dict[str, Any]:
    """Optimize resource allocation across projects."""
    optimization_results = {
        "current_allocation_efficiency": 0.0,
        "optimization_opportunities": [],
        "suggested_reallocations": [],
        "skill_matching_scores": {}
    }
    
    # Calculate current allocation efficiency
    total_effectiveness = 0
    total_allocations = 0
    
    for project in projects:
        if project.status not in ["completed", "cancelled"] and project.current_allocation:
            project_effectiveness = 0
            
            for allocation in project.current_allocation:
                resource_id = allocation.get("resource_id", "")
                hours = allocation.get("hours_per_week", 0)
                
                # Find the resource
                resource = next((r for r in resources if r.id == resource_id), None)
                if resource:
                    # Calculate effectiveness for this allocation
                    avg_skill_effectiveness = 0
                    skill_count = 0
                    
                    for skill in project.required_skills:
                        if skill in resource.skills:
                            avg_skill_effectiveness += resource.get_skill_effectiveness(skill)
                            skill_count += 1
                    
                    if skill_count > 0:
                        avg_skill_effectiveness /= skill_count
                        project_effectiveness += avg_skill_effectiveness * hours
                        total_allocations += hours
            
            if total_allocations > 0:
                total_effectiveness += project_effectiveness / total_allocations
    
    current_efficiency = total_effectiveness / max(len(projects), 1)
    optimization_results["current_allocation_efficiency"] = current_efficiency
    
    # Find optimization opportunities
    under_utilized = [r for r in resources if r.current_utilization < UTILIZATION_THRESHOLDS["under_utilized"]]
    over_allocated_projects = [p for p in projects if p.capacity_gap < 0 and p.status != "completed"]
    
    # Generate reallocation suggestions
    for project in projects:
        if project.capacity_gap > 0 and project.status != "completed":
            # Find best-fit under-utilized resources
            suitable_resources = []
            
            for resource in under_utilized:
                if resource.can_work_on_project(project.required_skills):
                    skill_match_score = 0
                    for skill in project.required_skills:
                        if skill in resource.skills:
                            skill_match_score += resource.get_skill_effectiveness(skill)
                    
                    skill_match_score /= max(len(project.required_skills), 1)
                    
                    suitable_resources.append({
                        "resource": resource,
                        "skill_match_score": skill_match_score,
                        "available_hours": resource.available_hours
                    })
            
            # Sort by skill match and availability
            suitable_resources.sort(key=lambda x: (x["skill_match_score"], x["available_hours"]), reverse=True)
            
            if suitable_resources:
                optimization_results["suggested_reallocations"].append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "gap_hours": project.capacity_gap,
                    "recommended_resources": suitable_resources[:3]  # Top 3 recommendations
                })
    
    return optimization_results
def _calculate_cost_impact(sim_resources: List[Resource], baseline_resources: List[Resource]) -> float:
    """Calculate cost impact of scenario vs baseline."""
    sim_cost = sum(r.hourly_rate * r.effective_hours_per_week for r in sim_resources)
    baseline_cost = sum(r.hourly_rate * r.effective_hours_per_week for r in baseline_resources)
    
    return sim_cost - baseline_cost

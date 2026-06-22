# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p2 import Project  # noqa: E402,E501
# fmt: on


def analyze_project_capacity_requirements(projects: List[Project]) -> Dict[str, Any]:
    """Analyze project capacity requirements and gaps."""
    project_stats = {
        "total_projects": len(projects),
        "active_projects": len([p for p in projects if p.status in ["active", "in_progress"]]),
        "planned_projects": len([p for p in projects if p.status == "planned"]),
        "total_estimated_hours": sum(p.adjusted_hours for p in projects),
        "total_weekly_demand": sum(p.required_hours_per_week for p in projects if p.status != "completed")
    }
    
    # Project priority analysis
    priority_distribution = {}
    for priority in ["high", "medium", "low"]:
        priority_projects = [p for p in projects if p.priority == priority]
        priority_distribution[priority] = {
            "count": len(priority_projects),
            "total_hours": sum(p.adjusted_hours for p in priority_projects),
            "weekly_demand": sum(p.required_hours_per_week for p in priority_projects if p.status != "completed")
        }
    
    # Capacity gap analysis
    projects_with_gaps = [p for p in projects if p.capacity_gap > 0 and p.status != "completed"]
    total_capacity_gap = sum(p.capacity_gap for p in projects_with_gaps)
    
    # Skill demand analysis
    skill_demand = {}
    for project in projects:
        if project.status != "completed":
            for skill, hours in project.skill_requirements.items():
                if skill not in skill_demand:
                    skill_demand[skill] = 0
                skill_demand[skill] += hours
    
    # Sort skills by demand
    sorted_skill_demand = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "project_stats": project_stats,
        "priority_distribution": priority_distribution,
        "capacity_gaps": {
            "projects_with_gaps": len(projects_with_gaps),
            "total_gap_hours_weekly": total_capacity_gap,
            "gap_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "priority": p.priority,
                    "gap_hours": p.capacity_gap,
                    "required_skills": p.required_skills
                }
                for p in sorted(projects_with_gaps, key=lambda p: p.capacity_gap, reverse=True)[:10]
            ]
        },
        "skill_demand": dict(sorted_skill_demand[:10])  # Top 10 skills in demand
    }

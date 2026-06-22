# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p1 import UTILIZATION_THRESHOLDS  # noqa: E402,E501
from resource_capacity_planner_p2 import Resource  # noqa: E402,E501
# fmt: on


def _generate_capacity_alerts(utilization_categories: Dict[str, List[Resource]]) -> List[str]:
    """Generate capacity-related alerts and warnings."""
    alerts = []
    
    critical_resources = utilization_categories.get("critical", [])
    over_utilized = utilization_categories.get("over_utilized", [])
    under_utilized = utilization_categories.get("under_utilized", [])
    
    if critical_resources:
        alerts.append(f"CRITICAL: {len(critical_resources)} resources are severely over-allocated (>95%)")
    
    if over_utilized:
        alerts.append(f"WARNING: {len(over_utilized)} resources are over-allocated (85-95%)")
    
    if len(under_utilized) > len(critical_resources) + len(over_utilized):
        alerts.append(f"OPPORTUNITY: {len(under_utilized)} resources are under-utilized (<60%)")
    
    return alerts
def analyze_resource_utilization(resources: List[Resource]) -> Dict[str, Any]:
    """Analyze current resource utilization and capacity."""
    utilization_stats = {
        "total_resources": len(resources),
        "total_capacity": sum(r.effective_hours_per_week for r in resources),
        "total_allocated": sum(r.effective_hours_per_week * r.current_utilization for r in resources),
        "total_available": sum(r.available_hours for r in resources)
    }
    
    # Calculate overall utilization
    utilization_stats["overall_utilization"] = (
        utilization_stats["total_allocated"] / max(utilization_stats["total_capacity"], 1)
    )
    
    # Categorize resources by utilization
    utilization_categories = {
        "under_utilized": [],
        "optimal": [],
        "over_utilized": [],
        "critical": []
    }
    
    for resource in resources:
        if resource.current_utilization <= UTILIZATION_THRESHOLDS["under_utilized"]:
            utilization_categories["under_utilized"].append(resource)
        elif resource.current_utilization <= UTILIZATION_THRESHOLDS["optimal"]:
            utilization_categories["optimal"].append(resource)
        elif resource.current_utilization <= UTILIZATION_THRESHOLDS["over_utilized"]:
            utilization_categories["over_utilized"].append(resource)
        else:
            utilization_categories["critical"].append(resource)
    
    # Role-based analysis
    role_analysis = {}
    for resource in resources:
        if resource.role not in role_analysis:
            role_analysis[resource.role] = {
                "count": 0,
                "total_capacity": 0,
                "average_utilization": 0,
                "available_hours": 0,
                "hourly_cost": 0
            }
        
        role_data = role_analysis[resource.role]
        role_data["count"] += 1
        role_data["total_capacity"] += resource.effective_hours_per_week
        role_data["available_hours"] += resource.available_hours
        role_data["hourly_cost"] += resource.hourly_rate
    
    # Calculate averages for roles
    for role in role_analysis:
        role_data = role_analysis[role]
        role_data["average_utilization"] = 1 - (role_data["available_hours"] / max(role_data["total_capacity"], 1))
        role_data["average_hourly_rate"] = role_data["hourly_cost"] / role_data["count"]
    
    return {
        "utilization_stats": utilization_stats,
        "utilization_categories": {
            k: [{"id": r.id, "name": r.name, "role": r.role, "utilization": r.current_utilization}
                for r in v]
            for k, v in utilization_categories.items()
        },
        "role_analysis": role_analysis,
        "capacity_alerts": _generate_capacity_alerts(utilization_categories)
    }

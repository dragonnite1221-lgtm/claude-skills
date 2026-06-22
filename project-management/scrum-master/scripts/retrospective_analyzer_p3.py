# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrospective_analyzer_base import *  # noqa: F403,E402
# fmt: off
from retrospective_analyzer_p2 import RetrospectiveData  # noqa: E402,E501
# fmt: on


def analyze_action_item_completion(retros: List[RetrospectiveData]) -> Dict[str, Any]:
    """Analyze action item completion rates and patterns."""
    all_action_items = []
    for retro in retros:
        all_action_items.extend(retro.action_items)
    
    if not all_action_items:
        return {
            "total_action_items": 0,
            "completion_rate": 0.0,
            "average_completion_time": 0.0
        }
    
    # Overall completion statistics
    completed_items = [item for item in all_action_items if item.is_completed]
    completion_rate = len(completed_items) / len(all_action_items)
    
    # Completion time analysis
    completion_times = []
    for item in completed_items:
        if item.completed_sprint and item.created_sprint:
            completion_time = item.completed_sprint - item.created_sprint
            if completion_time >= 0:
                completion_times.append(completion_time)
    
    avg_completion_time = statistics.mean(completion_times) if completion_times else 0.0
    
    # Status distribution
    status_counts = Counter(item.normalized_status for item in all_action_items)
    
    # Priority analysis
    priority_completion = {}
    for priority in ["high", "medium", "low"]:
        priority_items = [item for item in all_action_items if item.inferred_priority == priority]
        if priority_items:
            priority_completed = sum(1 for item in priority_items if item.is_completed)
            priority_completion[priority] = {
                "total": len(priority_items),
                "completed": priority_completed,
                "completion_rate": priority_completed / len(priority_items)
            }
    
    # Owner analysis
    owner_performance = defaultdict(lambda: {"total": 0, "completed": 0})
    for item in all_action_items:
        if item.owner:
            owner_performance[item.owner]["total"] += 1
            if item.is_completed:
                owner_performance[item.owner]["completed"] += 1
    
    for owner in owner_performance:
        owner_data = owner_performance[owner]
        owner_data["completion_rate"] = owner_data["completed"] / owner_data["total"]
    
    # Overdue items
    overdue_items = [item for item in all_action_items if item.is_overdue]
    
    return {
        "total_action_items": len(all_action_items),
        "completion_rate": completion_rate,
        "completed_items": len(completed_items),
        "average_completion_time": avg_completion_time,
        "status_distribution": dict(status_counts),
        "priority_analysis": priority_completion,
        "owner_performance": dict(owner_performance),
        "overdue_items": len(overdue_items),
        "overdue_rate": len(overdue_items) / len(all_action_items) if all_action_items else 0.0
    }
def _calculate_trend(values: List[float]) -> Dict[str, Any]:
    """Calculate trend direction and strength for a series of values."""
    if len(values) < 2:
        return {"direction": "insufficient_data", "strength": 0.0}
    
    # Simple linear regression
    n = len(values)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(values) / n
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    # Calculate correlation coefficient for trend strength
    try:
        correlation = statistics.correlation(x_values, values) if n > 2 else 0.0
    except statistics.StatisticsError:
        correlation = 0.0
    
    # Determine trend direction
    if abs(slope) < 0.01:  # Practically no change
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    return {
        "direction": direction,
        "slope": slope,
        "strength": abs(correlation),
        "correlation": correlation
    }

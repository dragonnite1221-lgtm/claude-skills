# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402
# fmt: off
from poc_planner_p1 import DEFAULT_EVAL_CATEGORIES, safe_divide  # noqa: E402,E501
# fmt: on


def generate_success_criteria(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate success criteria based on POC scope and requirements.

    Args:
        data: POC data with scope and requirements.

    Returns:
        List of success criteria with metrics.
    """
    criteria = []

    # Custom criteria from input
    custom_criteria = data.get("success_criteria", [])
    for cc in custom_criteria:
        criteria.append({
            "criterion": cc.get("criterion", "Unnamed criterion"),
            "metric": cc.get("metric", "Pass/Fail"),
            "target": cc.get("target", "Met"),
            "category": cc.get("category", "Functionality"),
            "priority": cc.get("priority", "must-have"),
        })

    # Auto-generated criteria based on scope
    scope_items = data.get("scope_items", [])
    for item in scope_items:
        if isinstance(item, str):
            criteria.append({
                "criterion": f"Validate: {item}",
                "metric": "Pass/Fail",
                "target": "Pass",
                "category": "Functionality",
                "priority": "must-have",
            })
        elif isinstance(item, dict):
            criteria.append({
                "criterion": item.get("name", "Unnamed scope item"),
                "metric": item.get("metric", "Pass/Fail"),
                "target": item.get("target", "Pass"),
                "category": item.get("category", "Functionality"),
                "priority": item.get("priority", "must-have"),
            })

    # Default criteria if none provided
    if not criteria:
        criteria = [
            {
                "criterion": "Core use case validation",
                "metric": "Percentage of use cases successfully demonstrated",
                "target": ">90%",
                "category": "Functionality",
                "priority": "must-have",
            },
            {
                "criterion": "Performance under expected load",
                "metric": "Response time at target concurrency",
                "target": "<2 seconds p95",
                "category": "Performance",
                "priority": "must-have",
            },
            {
                "criterion": "Integration with existing systems",
                "metric": "Number of integrations successfully tested",
                "target": "All planned integrations",
                "category": "Integration",
                "priority": "must-have",
            },
            {
                "criterion": "User acceptance",
                "metric": "Stakeholder satisfaction score",
                "target": ">4.0/5.0",
                "category": "Usability",
                "priority": "should-have",
            },
        ]

    return criteria
def generate_evaluation_scorecard(data: dict[str, Any]) -> dict[str, Any]:
    """Generate the POC evaluation scorecard template.

    Args:
        data: POC data.

    Returns:
        Evaluation scorecard structure.
    """
    custom_categories = data.get("evaluation_categories", {})

    # Merge custom categories with defaults
    categories = {}
    for cat_name, cat_data in DEFAULT_EVAL_CATEGORIES.items():
        if cat_name in custom_categories:
            custom = custom_categories[cat_name]
            categories[cat_name] = {
                "weight": custom.get("weight", cat_data["weight"]),
                "criteria": custom.get("criteria", cat_data["criteria"]),
                "score": None,
                "notes": "",
            }
        else:
            categories[cat_name] = {
                "weight": cat_data["weight"],
                "criteria": cat_data["criteria"],
                "score": None,
                "notes": "",
            }

    # Normalize weights to sum to 1.0
    total_weight = sum(c["weight"] for c in categories.values())
    if total_weight > 0 and abs(total_weight - 1.0) > 0.01:
        for cat in categories.values():
            cat["weight"] = round(safe_divide(cat["weight"], total_weight), 2)

    return {
        "scoring_scale": {
            "5": "Exceeds requirements - superior capability",
            "4": "Meets requirements - full capability",
            "3": "Partially meets - acceptable with minor gaps",
            "2": "Below expectations - significant gaps",
            "1": "Does not meet - critical gaps",
        },
        "categories": categories,
        "pass_threshold": 3.5,
        "strong_pass_threshold": 4.0,
    }

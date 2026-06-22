# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402


def estimate_resources(data: dict[str, Any], phases: list[dict[str, Any]]) -> dict[str, Any]:
    """Estimate resource requirements for the POC.

    Args:
        data: POC data with scope and requirements.
        phases: List of phase definitions.

    Returns:
        Resource allocation dictionary.
    """
    total_weeks = sum(p["duration_weeks"] for p in phases)
    complexity = data.get("complexity", "medium").lower()
    scope_items = data.get("scope_items", [])
    num_integrations = data.get("num_integrations", 0)

    # Base SE hours per week by complexity
    se_hours_per_week = {"low": 15, "medium": 25, "high": 35}.get(complexity, 25)

    # Engineering support hours
    eng_base = {"low": 5, "medium": 10, "high": 20}.get(complexity, 10)
    eng_integration_hours = num_integrations * 8

    # Customer resource hours
    customer_hours_per_week = {"low": 5, "medium": 8, "high": 12}.get(complexity, 8)

    se_total = se_hours_per_week * total_weeks
    eng_total = (eng_base * total_weeks) + eng_integration_hours
    customer_total = customer_hours_per_week * total_weeks

    # Phase-level breakdown
    phase_resources = []
    for phase in phases:
        weeks = phase["duration_weeks"]
        # Setup phase has higher SE and eng effort
        se_multiplier = 1.3 if phase["name"] == "Setup" else (
            1.0 if phase["name"] in ("Core Testing", "Advanced Testing") else 0.7
        )
        eng_multiplier = 1.5 if phase["name"] == "Setup" else (
            1.0 if phase["name"] == "Core Testing" else (
                1.2 if phase["name"] == "Advanced Testing" else 0.5
            )
        )

        phase_resources.append({
            "phase": phase["name"],
            "duration_weeks": weeks,
            "se_hours": round(se_hours_per_week * weeks * se_multiplier),
            "engineering_hours": round(eng_base * weeks * eng_multiplier),
            "customer_hours": round(customer_hours_per_week * weeks),
        })

    return {
        "total_duration_weeks": total_weeks,
        "complexity": complexity,
        "totals": {
            "se_hours": se_total,
            "engineering_hours": eng_total,
            "customer_hours": customer_total,
            "total_hours": se_total + eng_total + customer_total,
        },
        "phase_breakdown": phase_resources,
        "additional_resources": {
            "integration_hours": eng_integration_hours,
            "num_integrations": num_integrations,
        },
    }

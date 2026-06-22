# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402


ROLE_TYPES = {
    "senior_engineer": {
        "hourly_rate": 150,
        "efficiency_factor": 1.2,
        "skill_multipliers": {
            "backend": 1.0,
            "frontend": 0.9,
            "mobile": 0.8,
            "devops": 1.1,
            "data": 0.9
        }
    },
    "mid_engineer": {
        "hourly_rate": 100,
        "efficiency_factor": 1.0,
        "skill_multipliers": {
            "backend": 1.0,
            "frontend": 1.0,
            "mobile": 0.9,
            "devops": 0.8,
            "data": 0.8
        }
    },
    "junior_engineer": {
        "hourly_rate": 70,
        "efficiency_factor": 0.7,
        "skill_multipliers": {
            "backend": 0.8,
            "frontend": 0.9,
            "mobile": 0.7,
            "devops": 0.6,
            "data": 0.7
        }
    },
    "product_manager": {
        "hourly_rate": 130,
        "efficiency_factor": 1.1,
        "skill_multipliers": {
            "planning": 1.0,
            "stakeholder_mgmt": 1.0,
            "analysis": 0.9
        }
    },
    "designer": {
        "hourly_rate": 90,
        "efficiency_factor": 1.0,
        "skill_multipliers": {
            "ui_design": 1.0,
            "ux_research": 1.0,
            "prototyping": 0.9
        }
    },
    "qa_engineer": {
        "hourly_rate": 80,
        "efficiency_factor": 0.9,
        "skill_multipliers": {
            "manual_testing": 1.0,
            "automation": 1.1,
            "performance": 0.9
        }
    }
}
UTILIZATION_THRESHOLDS = {
    "under_utilized": 0.60,   # Below 60%
    "optimal": 0.85,          # 60-85%
    "over_utilized": 0.95,    # 85-95%
    "critical": 1.0           # Above 95%
}
CAPACITY_FACTORS = {
    "meeting_overhead": 0.15,     # 15% for meetings
    "learning_development": 0.05,  # 5% for skill development
    "administrative": 0.10,       # 10% for admin tasks
    "context_switching": 0.05,    # 5% for project switching penalty
    "vacation_sick": 0.12         # 12% for time off
}
PROJECT_COMPLEXITY_FACTORS = {
    "simple": 1.0,
    "moderate": 1.2,
    "complex": 1.5,
    "very_complex": 2.0
}

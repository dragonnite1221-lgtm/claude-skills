# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p7 import _mod_cg1_0  # noqa: E402,E501
# fmt: on


def _mod_cg1_1():
    return [
        {
            "name": "Engineering Deployment",
            "category": "Engineering",
            "maturity": {
                "documentation": 4,
                "ownership": 5,
                "metrics": 4,
                "automation": 4,
                "consistency": 5,
                "feedback_loop": 4,
            },
            "steps": [
                {
                    "name": "PR submitted",
                    "throughput_per_day": 20,
                    "capacity_per_day": 25,
                    "current_queue": 8,
                    "avg_wait_hours": 3,
                    "avg_process_hours": 2,
                },
                {
                    "name": "Code review",
                    "throughput_per_day": 18,
                    "capacity_per_day": 22,
                    "current_queue": 10,
                    "avg_wait_hours": 4,
                    "avg_process_hours": 1,
                },
                {
                    "name": "CI pipeline",
                    "throughput_per_day": 18,
                    "capacity_per_day": 30,
                    "current_queue": 2,
                    "avg_wait_hours": 0.5,
                    "avg_process_hours": 0.5,
                },
                {
                    "name": "Deploy to production",
                    "throughput_per_day": 16,
                    "capacity_per_day": 20,
                    "current_queue": 1,
                    "avg_wait_hours": 0.5,
                    "avg_process_hours": 0.25,
                },
            ],
        },
        {
            "name": "Incident Response",
            "category": "Engineering / Operations",
            "maturity": {
                "documentation": 2,
                "ownership": 2,
                "metrics": 1,
                "automation": 1,
                "consistency": 2,
                "feedback_loop": 1,
            },
            "steps": [],
        },
        {
            "name": "Employee Onboarding",
            "category": "People",
            "maturity": {
                "documentation": 2,
                "ownership": 2,
                "metrics": 1,
                "automation": 1,
                "consistency": 2,
                "feedback_loop": 2,
            },
            "steps": [],
        },
        {
            "name": "Vendor Procurement",
            "category": "Operations",
            "maturity": {
                "documentation": 1,
                "ownership": 1,
                "metrics": 0,
                "automation": 0,
                "consistency": 1,
                "feedback_loop": 0,
            },
            "steps": [],
        },
    ]
def _mod_cg0_1():
    return {
        "processes": (_mod_cg1_0() + _mod_cg1_1()),
    }

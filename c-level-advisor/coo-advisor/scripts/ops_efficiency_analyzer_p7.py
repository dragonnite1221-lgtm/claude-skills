# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p2 import score_process_maturity  # noqa: E402,E501
from ops_efficiency_analyzer_p3 import analyze_bottlenecks  # noqa: E402,E501
from ops_efficiency_analyzer_p4 import analyze_team_structure  # noqa: E402,E501
from ops_efficiency_analyzer_p5 import generate_improvement_plan  # noqa: E402,E501
from ops_efficiency_analyzer_p6 import format_report  # noqa: E402,E501
# fmt: on


def run_analysis(data: dict) -> str:
    """Run the full analysis pipeline on input data."""
    processes = data.get("processes", [])
    team = data.get("team", {})
    metrics = data.get("metrics", {})

    # 1. Score process maturity
    process_scores = [score_process_maturity(p) for p in processes]

    # 2. Analyze bottlenecks
    bottleneck_analysis = analyze_bottlenecks(processes)

    # 3. Analyze team structure
    team_analysis = analyze_team_structure(team)

    # 4. Generate improvement plan
    improvement_plan = generate_improvement_plan(
        process_scores, bottleneck_analysis, team_analysis, metrics
    )

    # 5. Format and return report
    return format_report(
        process_scores, bottleneck_analysis, team_analysis, improvement_plan, metrics
    )
def _mod_cg0_0():
    return {
        "company": "AcmeSaaS",
        "stage": "series_b",
        "metrics": {
        "annual_revenue_usd": 18000000,
        "burn_multiple": 1.8,
        "net_revenue_retention_pct": 108,
        "cac_payback_months": 14,
        "headcount": 85,
        "monthly_churn_pct": 1.2,
    },
    }
def _mod_cg1_0():
    return [
        {
            "name": "Customer Onboarding",
            "category": "Customer Success",
            "maturity": {
                "documentation": 3,
                "ownership": 4,
                "metrics": 3,
                "automation": 2,
                "consistency": 3,
                "feedback_loop": 2,
            },
            "steps": [
                {
                    "name": "Contract signed → kickoff scheduled",
                    "throughput_per_day": 4,
                    "capacity_per_day": 6,
                    "current_queue": 3,
                    "avg_wait_hours": 4,
                    "avg_process_hours": 1,
                },
                {
                    "name": "Technical setup & integration",
                    "throughput_per_day": 2,
                    "capacity_per_day": 3,
                    "current_queue": 8,
                    "avg_wait_hours": 24,
                    "avg_process_hours": 8,
                },
                {
                    "name": "Training & enablement",
                    "throughput_per_day": 3,
                    "capacity_per_day": 4,
                    "current_queue": 2,
                    "avg_wait_hours": 8,
                    "avg_process_hours": 4,
                },
                {
                    "name": "Go-live confirmation",
                    "throughput_per_day": 4,
                    "capacity_per_day": 6,
                    "current_queue": 1,
                    "avg_wait_hours": 2,
                    "avg_process_hours": 1,
                },
            ],
        },
        {
            "name": "Sales Deal Qualification",
            "category": "Sales",
            "maturity": {
                "documentation": 2,
                "ownership": 3,
                "metrics": 4,
                "automation": 2,
                "consistency": 2,
                "feedback_loop": 3,
            },
            "steps": [
                {
                    "name": "Inbound lead review",
                    "throughput_per_day": 15,
                    "capacity_per_day": 20,
                    "current_queue": 5,
                    "avg_wait_hours": 2,
                    "avg_process_hours": 0.5,
                },
                {
                    "name": "BANT qualification call",
                    "throughput_per_day": 8,
                    "capacity_per_day": 10,
                    "current_queue": 12,
                    "avg_wait_hours": 24,
                    "avg_process_hours": 1,
                },
                {
                    "name": "Demo scheduling & prep",
                    "throughput_per_day": 6,
                    "capacity_per_day": 8,
                    "current_queue": 4,
                    "avg_wait_hours": 8,
                    "avg_process_hours": 0.5,
                },
            ],
        },
    ]

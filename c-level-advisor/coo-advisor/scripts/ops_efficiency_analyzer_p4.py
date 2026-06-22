# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p1 import TeamData  # noqa: E402,E501
from ops_efficiency_analyzer_p3 import _dept_revenue_benchmark, _expected_layers  # noqa: E402,E501
# fmt: on


def _efficiency_status(efficiency_pct: Optional[float]) -> str:
    if efficiency_pct is None:
        return "N/A"
    if efficiency_pct >= 90:
        return "🟢 On benchmark"
    elif efficiency_pct >= 70:
        return "🟡 Below benchmark"
    else:
        return "🔴 Significantly below"
def analyze_team_structure(team: TeamData) -> dict[str, Any]:
    """
    Analyze team structure for span of control, layer count, and hiring gaps.
    """
    issues = []
    recommendations = []
    warnings = []

    total_headcount = team.get("total_headcount", 0)
    departments = team.get("departments", [])

    # Span of control analysis
    span_issues = []
    for dept in departments:
        for manager in dept.get("managers", []):
            direct_reports = manager.get("direct_reports", 0)
            manages_managers = manager.get("manages_managers", False)

            optimal_min = 3 if manages_managers else 5
            optimal_max = 5 if manages_managers else 8

            if direct_reports < optimal_min:
                span_issues.append({
                    "manager": manager["name"],
                    "dept": dept["name"],
                    "reports": direct_reports,
                    "issue": "Under-span",
                    "recommendation": f"Merge team or promote ICs — {direct_reports} reports is management overhead",
                })
            elif direct_reports > optimal_max:
                span_issues.append({
                    "manager": manager["name"],
                    "dept": dept["name"],
                    "reports": direct_reports,
                    "issue": "Over-span",
                    "recommendation": f"Split team — {direct_reports} reports means minimal 1:1 time and poor feedback loops",
                })

    # Management layers analysis
    max_layers = team.get("management_layers", 0)
    expected_layers = _expected_layers(total_headcount)
    if max_layers > expected_layers + 1:
        issues.append({
            "type": "Over-layered",
            "detail": f"{max_layers} management layers for {total_headcount} people. "
                      f"Expected: {expected_layers}. Excess layers slow decisions.",
            "recommendation": "Flatten: remove middle management layers that don't add decision value",
        })

    # Revenue per employee by department
    annual_revenue = team.get("annual_revenue_usd", 0)
    dept_analysis = []
    for dept in departments:
        headcount = dept.get("headcount", 0)
        if headcount > 0 and annual_revenue > 0:
            rev_per_employee = annual_revenue / headcount
            benchmark = _dept_revenue_benchmark(dept["name"], team.get("stage", "series_a"))
            efficiency_pct = (rev_per_employee / benchmark * 100) if benchmark > 0 else None

            dept_analysis.append({
                "department": dept["name"],
                "headcount": headcount,
                "revenue_per_employee": round(rev_per_employee),
                "benchmark": benchmark,
                "efficiency_vs_benchmark_pct": round(efficiency_pct, 1) if efficiency_pct else "N/A",
                "status": _efficiency_status(efficiency_pct),
            })

    # Open req health
    open_reqs = team.get("open_requisitions", 0)
    req_to_headcount_ratio = (open_reqs / total_headcount * 100) if total_headcount > 0 else 0
    if req_to_headcount_ratio > 20:
        warnings.append(
            f"High open req ratio: {open_reqs} open reqs against {total_headcount} headcount "
            f"({req_to_headcount_ratio:.0f}%). This level of hiring while operating is operationally disruptive."
        )

    return {
        "total_headcount": total_headcount,
        "management_layers": max_layers,
        "expected_layers": expected_layers,
        "span_of_control_issues": span_issues,
        "structural_issues": issues,
        "department_efficiency": dept_analysis,
        "open_req_health": {
            "open_reqs": open_reqs,
            "ratio_pct": round(req_to_headcount_ratio, 1),
            "warnings": warnings,
        },
    }

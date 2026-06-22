# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_plan_modeler_base import *  # noqa: F403,E402
# fmt: off
from hiring_plan_modeler_p1 import HiringPlan, compute_hire_costs, get_quarters  # noqa: E402,E501
# fmt: on


def assess_risks(plan: HiringPlan, totals: dict) -> list[dict]:
    risks = []

    # Headcount growth too fast
    growth_pct = totals["headcount_growth_pct"]
    if growth_pct > 80:
        risks.append({
            "severity": "HIGH",
            "category": "Execution",
            "finding": f"Headcount growing {growth_pct:.0f}% this period. "
                       "Culture and processes rarely scale this fast without breakage.",
            "recommendation": "Stagger Q3/Q4 hires. Validate Q1/Q2 cohort is onboarded before next wave."
        })
    elif growth_pct > 50:
        risks.append({
            "severity": "MEDIUM",
            "category": "Execution",
            "finding": f"Headcount growing {growth_pct:.0f}% — significant scaling challenge.",
            "recommendation": "Ensure onboarding infrastructure scales. Assign buddy/mentor to each hire."
        })

    # High concentration in one quarter
    quarters = get_quarters(plan.hires)
    q_counts = {q: sum(1 for h in plan.hires if h.quarter == q) for q in quarters}
    max_q = max(q_counts.values()) if q_counts else 0
    if max_q > len(plan.hires) * 0.5 and max_q > 4:
        heavy_q = [q for q, c in q_counts.items() if c == max_q][0]
        risks.append({
            "severity": "MEDIUM",
            "category": "Hiring Execution",
            "finding": f"More than 50% of hires planned in {heavy_q} ({max_q} hires). "
                       "Recruiting capacity and onboarding bandwidth may be insufficient.",
            "recommendation": "Spread hires across quarters. Hiring pipeline needs to start 60–90 days before target start date."
        })

    # Revenue per employee declining
    if totals["revenue_per_employee_target"] < totals["revenue_per_employee_current"] * 0.7:
        risks.append({
            "severity": "HIGH",
            "category": "Financial",
            "finding": f"Revenue per employee declining from ${totals['revenue_per_employee_current']:,.0f} to "
                       f"${totals['revenue_per_employee_target']:,.0f} — a {((totals['revenue_per_employee_target']/totals['revenue_per_employee_current'])-1)*100:.0f}% drop.",
            "recommendation": "Validate that revenue model supports this headcount. Is target revenue achievable with this team?"
        })

    # Low priority hires consuming budget
    low_priority_hires = [h for h in plan.hires if h.priority == "Low"]
    if low_priority_hires:
        lp_cost = sum(compute_hire_costs(h)["first_year_total"] for h in low_priority_hires)
        risks.append({
            "severity": "MEDIUM",
            "category": "Prioritization",
            "finding": f"{len(low_priority_hires)} 'Low' priority hires consuming ${lp_cost:,.0f} in first-year costs.",
            "recommendation": "Consider deferring Low priority hires to preserve runway. Cut these first if budget tightens."
        })

    # Hires without business cases
    no_case = [h for h in plan.hires if not h.business_case]
    if no_case:
        risks.append({
            "severity": "MEDIUM",
            "category": "Governance",
            "finding": f"{len(no_case)} hires have no documented business case: {', '.join(h.role for h in no_case[:5])}{'...' if len(no_case) > 5 else ''}",
            "recommendation": "Every hire over $80K should have a written business case. What revenue or risk does this role address?"
        })

    # High recruiter fee exposure
    if totals["total_recruiter_fees"] > 100_000:
        risks.append({
            "severity": "LOW",
            "category": "Cost",
            "finding": f"${totals['total_recruiter_fees']:,.0f} in recruiter fees. "
                       "Consider whether internal recruiter investment would be cheaper at this hiring volume.",
            "recommendation": f"Internal recruiter at $120–150K fully loaded pays off at 3–4 hires/year vs. agency fees."
        })

    # No risks — that's itself a flag
    if not risks:
        risks.append({
            "severity": "INFO",
            "category": "General",
            "finding": "No major risks flagged. Plan appears well-structured.",
            "recommendation": "Validate assumptions: time-to-fill estimates, revenue model, and Q1 hiring pipeline status."
        })

    return risks
def fmt(n: int) -> str:
    return f"${n:,.0f}"
def pct(n: float) -> str:
    return f"{n:.1f}%"

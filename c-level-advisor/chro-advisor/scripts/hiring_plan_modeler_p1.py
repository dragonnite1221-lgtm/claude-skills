# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_plan_modeler_base import *  # noqa: F403,E402


@dataclass
class HireTarget:
    """One planned hire."""
    role: str
    level: str              # L1, L2, L3, L4, M1, M2, M3, VP, C-Suite
    function: str           # Engineering, Sales, Product, G&A, Marketing, CS
    quarter: str            # Q1-2025, Q2-2025, etc.
    base_salary: int        # Annual, USD
    bonus_pct: float        # % of base (e.g., 0.10 for 10%)
    equity_annual_usd: int  # Annualized equity value at current 409A
    benefits_annual: int    # Employer-paid benefits
    recruiter_fee_pct: float= 0.20  # Agency fee if used (0 for internal recruiter)
    ramp_months: int        = 3     # Months to full productivity
    priority: str           = "High"  # High / Medium / Low
    business_case: str      = ""
    open_to_internal: bool  = False
@dataclass
class HiringPlan:
    company: str
    plan_period: str        # e.g., "2025 Annual"
    current_headcount: int
    target_revenue: int     # Annual target revenue ($)
    current_revenue: int    # Current ARR ($)
    hires: list[HireTarget] = field(default_factory=list)

    # Cost overheads beyond comp
    overhead_rate: float = 0.25     # Workspace, software, onboarding overhead as % of base
    internal_recruiter_cost: int = 0  # If you have an internal recruiter, annual cost
def quarter_to_sortkey(q: str) -> tuple[int, int]:
    """Parse 'Q2-2025' → (2025, 2)"""
    parts = q.upper().split("-")
    if len(parts) == 2:
        q_num = int(parts[0].replace("Q", ""))
        year = int(parts[1])
        return (year, q_num)
    return (9999, 9)
def get_quarters(hires: list[HireTarget]) -> list[str]:
    """Return sorted unique quarters from hire list."""
    quarters = sorted(set(h.quarter for h in hires), key=quarter_to_sortkey)
    return quarters
def compute_hire_costs(hire: HireTarget) -> dict:
    """Compute total first-year cost for one hire."""
    total_comp = hire.base_salary + int(hire.base_salary * hire.bonus_pct) + hire.equity_annual_usd + hire.benefits_annual
    recruiter_fee = int(hire.base_salary * hire.recruiter_fee_pct)
    overhead = int(hire.base_salary * 0.25)  # workspace, tools, onboarding
    ramp_productivity_cost = int(hire.base_salary * (hire.ramp_months / 12))  # cost during ramp

    return {
        "base_salary": hire.base_salary,
        "target_bonus": int(hire.base_salary * hire.bonus_pct),
        "equity_annual": hire.equity_annual_usd,
        "benefits": hire.benefits_annual,
        "total_comp": total_comp,
        "recruiter_fee": recruiter_fee,
        "overhead": overhead,
        "ramp_cost": ramp_productivity_cost,
        "first_year_total": total_comp + recruiter_fee + overhead,
        "fully_loaded_first_year": total_comp + recruiter_fee + overhead + ramp_productivity_cost,
    }
def summarize_by_quarter(plan: HiringPlan) -> dict[str, dict]:
    """Aggregate headcount and costs per quarter."""
    quarters = get_quarters(plan.hires)
    summary = {}
    running_headcount = plan.current_headcount

    for q in quarters:
        q_hires = [h for h in plan.hires if h.quarter == q]
        q_costs = [compute_hire_costs(h) for h in q_hires]

        total_comp = sum(c["total_comp"] for c in q_costs)
        total_first_year = sum(c["first_year_total"] for c in q_costs)
        recruiter_fees = sum(c["recruiter_fee"] for c in q_costs)

        running_headcount += len(q_hires)

        summary[q] = {
            "new_hires": len(q_hires),
            "headcount_eop": running_headcount,
            "total_annual_comp_added": total_comp,
            "total_first_year_cost": total_first_year,
            "recruiter_fees": recruiter_fees,
            "hires": q_hires,
            "costs": q_costs,
        }

    return summary
def summarize_by_function(plan: HiringPlan) -> dict[str, dict]:
    """Aggregate headcount and costs per function."""
    functions: dict[str, dict] = {}
    for hire in plan.hires:
        fn = hire.function
        if fn not in functions:
            functions[fn] = {"count": 0, "total_comp": 0, "total_first_year": 0, "roles": []}
        costs = compute_hire_costs(hire)
        functions[fn]["count"] += 1
        functions[fn]["total_comp"] += costs["total_comp"]
        functions[fn]["total_first_year"] += costs["first_year_total"]
        functions[fn]["roles"].append(hire.role)
    return functions
def compute_totals(plan: HiringPlan) -> dict:
    all_costs = [compute_hire_costs(h) for h in plan.hires]
    total_hires = len(plan.hires)
    total_comp = sum(c["total_comp"] for c in all_costs)
    total_first_year = sum(c["first_year_total"] for c in all_costs)
    total_fully_loaded = sum(c["fully_loaded_first_year"] for c in all_costs)
    total_recruiter = sum(c["recruiter_fee"] for c in all_costs)

    final_headcount = plan.current_headcount + total_hires
    revenue_per_employee = plan.target_revenue / final_headcount if final_headcount > 0 else 0
    revenue_per_employee_current = plan.current_revenue / plan.current_headcount if plan.current_headcount > 0 else 0

    return {
        "total_hires": total_hires,
        "final_headcount": final_headcount,
        "headcount_growth_pct": ((final_headcount - plan.current_headcount) / plan.current_headcount * 100) if plan.current_headcount > 0 else 0,
        "total_annual_comp_added": total_comp,
        "total_first_year_cost": total_first_year,
        "total_fully_loaded_first_year": total_fully_loaded,
        "total_recruiter_fees": total_recruiter,
        "revenue_per_employee_target": revenue_per_employee,
        "revenue_per_employee_current": revenue_per_employee_current,
        "avg_comp_per_hire": total_comp // total_hires if total_hires > 0 else 0,
    }

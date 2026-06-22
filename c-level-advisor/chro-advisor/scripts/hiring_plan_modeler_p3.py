# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_plan_modeler_base import *  # noqa: F403,E402
# fmt: off
from hiring_plan_modeler_p1 import HiringPlan, compute_hire_costs, compute_totals, quarter_to_sortkey, summarize_by_function, summarize_by_quarter  # noqa: E402,E501
from hiring_plan_modeler_p2 import assess_risks, fmt  # noqa: E402,E501
# fmt: on


def print_report(plan: HiringPlan):
    WIDTH = 72
    SEP = "=" * WIDTH
    sep = "-" * WIDTH

    print(SEP)
    print(f"  HIRING PLAN: {plan.company}")
    print(f"  Period: {plan.plan_period}  |  Generated: {date.today().isoformat()}")
    print(SEP)

    totals = compute_totals(plan)
    q_summary = summarize_by_quarter(plan)
    fn_summary = summarize_by_function(plan)
    risks = assess_risks(plan, totals)

    # Executive summary
    print("\n[ EXECUTIVE SUMMARY ]")
    print(sep)
    print(f"  Current headcount:       {plan.current_headcount:>5}")
    print(f"  Planned hires:           {totals['total_hires']:>5}")
    print(f"  Final headcount:         {totals['final_headcount']:>5}  (+{totals['headcount_growth_pct']:.0f}%)")
    print(f"  Current ARR:             {fmt(plan.current_revenue):>12}")
    print(f"  Target revenue:          {fmt(plan.target_revenue):>12}")
    print(f"  Revenue/employee now:    {fmt(int(totals['revenue_per_employee_current'])):>12}")
    print(f"  Revenue/employee target: {fmt(int(totals['revenue_per_employee_target'])):>12}")
    print()
    print(f"  Total annual comp added: {fmt(totals['total_annual_comp_added']):>12}")
    print(f"  Total first-year cost:   {fmt(totals['total_first_year_cost']):>12}")
    print(f"  Fully loaded (w/ ramp):  {fmt(totals['total_fully_loaded_first_year']):>12}")
    print(f"  Recruiter fees:          {fmt(totals['total_recruiter_fees']):>12}")
    print(f"  Avg comp per hire:       {fmt(totals['avg_comp_per_hire']):>12}")

    # Quarterly breakdown
    print(f"\n[ QUARTERLY HEADCOUNT PLAN ]")
    print(sep)
    print(f"  {'Quarter':<10} {'New Hires':>10} {'HC (EOP)':>10} {'Comp Added':>14} {'1yr Cost':>14} {'Recruiter $':>12}")
    print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*14} {'-'*14} {'-'*12}")
    for q, data in q_summary.items():
        print(f"  {q:<10} {data['new_hires']:>10} {data['headcount_eop']:>10} "
              f"{fmt(data['total_annual_comp_added']):>14} "
              f"{fmt(data['total_first_year_cost']):>14} "
              f"{fmt(data['recruiter_fees']):>12}")

    # By function
    print(f"\n[ HEADCOUNT BY FUNCTION ]")
    print(sep)
    print(f"  {'Function':<18} {'Hires':>7} {'Annual Comp':>14} {'1yr Cost':>14}")
    print(f"  {'-'*18} {'-'*7} {'-'*14} {'-'*14}")
    for fn, data in sorted(fn_summary.items(), key=lambda x: -x[1]["count"]):
        print(f"  {fn:<18} {data['count']:>7} {fmt(data['total_comp']):>14} {fmt(data['total_first_year']):>14}")

    # Hire detail
    print(f"\n[ HIRE DETAIL ]")
    print(sep)
    print(f"  {'Role':<30} {'Fn':<14} {'Lvl':<6} {'Q':<8} {'Base':>10} {'Total Comp':>12} {'Priority':<8}")
    print(f"  {'-'*30} {'-'*14} {'-'*6} {'-'*8} {'-'*10} {'-'*12} {'-'*8}")
    for h in sorted(plan.hires, key=lambda x: quarter_to_sortkey(x.quarter)):
        costs = compute_hire_costs(h)
        print(f"  {h.role:<30} {h.function:<14} {h.level:<6} {h.quarter:<8} "
              f"{fmt(h.base_salary):>10} {fmt(costs['total_comp']):>12} {h.priority:<8}")
        if h.business_case:
            bc = h.business_case[:60] + "..." if len(h.business_case) > 60 else h.business_case
            print(f"  {'':>30}   ↳ {bc}")

    # Risk assessment
    print(f"\n[ RISK ASSESSMENT ]")
    print(sep)
    sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    for risk in sorted(risks, key=lambda r: sev_order.get(r["severity"], 99)):
        sev = risk["severity"]
        marker = {"HIGH": "⚠ HIGH", "MEDIUM": "◆ MED ", "LOW": "◇ LOW ", "INFO": "ℹ INFO"}[sev]
        print(f"\n  [{marker}] {risk['category']}")
        # Wrap finding
        finding = risk["finding"]
        words = finding.split()
        line = "  Finding: "
        for w in words:
            if len(line) + len(w) + 1 > WIDTH - 2:
                print(line)
                line = "           " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(line)
        reco = risk["recommendation"]
        words = reco.split()
        line = "  Action:  "
        for w in words:
            if len(line) + len(w) + 1 > WIDTH - 2:
                print(line)
                line = "           " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(line)

    print(f"\n{SEP}\n")
def export_csv(plan: HiringPlan) -> str:
    """Return CSV of hire detail."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Role", "Function", "Level", "Quarter", "Priority",
                     "Base Salary", "Bonus Target", "Equity Annual", "Benefits",
                     "Total Comp", "Recruiter Fee", "Overhead", "First Year Total",
                     "Ramp Months", "Open to Internal", "Business Case"])
    for h in plan.hires:
        c = compute_hire_costs(h)
        writer.writerow([h.role, h.function, h.level, h.quarter, h.priority,
                         h.base_salary, c["target_bonus"], h.equity_annual_usd, h.benefits_annual,
                         c["total_comp"], c["recruiter_fee"], c["overhead"], c["first_year_total"],
                         h.ramp_months, h.open_to_internal, h.business_case])
    return output.getvalue()

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_simulator_base import *  # noqa: F403,E402


def simulate(
    mrr,
    monthly_growth_pct,
    monthly_churn_pct,
    cac,
    gross_margin=0.70,
    sm_spend_pct=0.30,
    months=12,
):
    """
    Simulate unit economics forward.
    
    Args:
        mrr: Starting MRR
        monthly_growth_pct: Expected monthly growth rate (%)
        monthly_churn_pct: Expected monthly churn rate (%)
        cac: Customer acquisition cost
        gross_margin: Gross margin (0-1)
        sm_spend_pct: Sales & marketing as % of revenue (0-1)
        months: Number of months to project
    
    Returns:
        dict with monthly projections and summary
    """
    results = {
        "inputs": {
            "starting_mrr": mrr,
            "monthly_growth_pct": monthly_growth_pct,
            "monthly_churn_pct": monthly_churn_pct,
            "cac": cac,
            "gross_margin": gross_margin,
            "sm_spend_pct": sm_spend_pct,
        },
        "projections": [],
        "summary": {},
    }
    
    current_mrr = mrr
    cumulative_sm_spend = 0
    cumulative_gross_profit = 0
    
    for month in range(1, months + 1):
        # Calculate growth and churn
        growth_rate = monthly_growth_pct / 100
        churn_rate = monthly_churn_pct / 100
        
        # Net growth = growth - churn
        net_growth_rate = growth_rate - churn_rate
        new_mrr = current_mrr * (1 + net_growth_rate)
        
        # Revenue and costs
        monthly_revenue = current_mrr
        gross_profit = monthly_revenue * gross_margin
        sm_spend = monthly_revenue * sm_spend_pct
        net_profit = gross_profit - sm_spend
        
        # Accumulate
        cumulative_sm_spend += sm_spend
        cumulative_gross_profit += gross_profit
        
        # ARR
        arr = current_mrr * 12
        
        results["projections"].append({
            "month": month,
            "mrr": round(current_mrr, 2),
            "arr": round(arr, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "gross_profit": round(gross_profit, 2),
            "sm_spend": round(sm_spend, 2),
            "net_profit": round(net_profit, 2),
            "growth_rate_pct": round(net_growth_rate * 100, 2),
        })
        
        current_mrr = new_mrr
    
    # Summary
    final_mrr = results["projections"][-1]["mrr"]
    final_arr = results["projections"][-1]["arr"]
    total_revenue = sum(p["monthly_revenue"] for p in results["projections"])
    total_net_profit = sum(p["net_profit"] for p in results["projections"])
    
    results["summary"] = {
        "starting_mrr": mrr,
        "ending_mrr": round(final_mrr, 2),
        "ending_arr": round(final_arr, 2),
        "mrr_growth_pct": round(((final_mrr - mrr) / mrr) * 100, 2),
        "total_revenue_12m": round(total_revenue, 2),
        "total_gross_profit_12m": round(cumulative_gross_profit, 2),
        "total_sm_spend_12m": round(cumulative_sm_spend, 2),
        "total_net_profit_12m": round(total_net_profit, 2),
        "avg_monthly_growth_pct": round((monthly_growth_pct - monthly_churn_pct), 2),
    }
    
    return results

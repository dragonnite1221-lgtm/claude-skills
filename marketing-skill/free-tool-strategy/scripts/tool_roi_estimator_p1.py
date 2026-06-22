# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_roi_estimator_base import *  # noqa: F403,E402


def traffic_at_month(params, month):
    """
    Traffic grows from near-zero during SEO ramp, then compounds.
    Month 1 = launch spike (Product Hunt / HN etc.) if ramp=0, or baseline.
    """
    ramp = params.get("seo_ramp_months", 3)
    base = params["traffic_month_1"]
    growth = params["traffic_growth_rate"]

    if month <= ramp:
        # Linear ramp to base traffic during SEO warmup
        return round(base * (month / ramp), 0) if ramp > 0 else base
    else:
        # Compound growth after ramp
        months_since_ramp = month - ramp
        return round(base * ((1 + growth) ** months_since_ramp), 0)
def leads_at_month(params, sessions):
    completion_rate = params["tool_completion_rate"]
    lead_capture_rate = params["lead_capture_rate"]
    completions = sessions * completion_rate
    leads = completions * lead_capture_rate
    return round(leads, 1)
def customers_at_month(params, leads):
    trial_rate = params["lead_to_trial_rate"]
    paid_rate = params["trial_to_paid_rate"]
    customers = leads * trial_rate * paid_rate
    return round(customers, 2)
def revenue_at_month(params, customers):
    return round(customers * params["ltv"], 2)
def cost_at_month(params, month):
    """
    Month 1: build cost + maintenance.
    Subsequent months: maintenance only.
    """
    maintenance = params["monthly_maintenance"]
    backlink_value = params.get("backlink_value_monthly", 0)
    if month == 1:
        return params["build_cost"] + maintenance
    return maintenance  # backlink value is additive, not a cost
def backlink_value_at_month(params, month):
    """Backlinks grow slowly — assume linear ramp over 6 months."""
    max_val = params.get("backlink_value_monthly", 0)
    ramp = 6
    if month >= ramp:
        return max_val
    return round(max_val * (month / ramp), 2)
def build_projection(params):
    months = params["months_to_model"]
    rows = []
    cumulative_cost = 0
    cumulative_revenue = 0
    cumulative_backlink_value = 0

    for m in range(1, months + 1):
        sessions = traffic_at_month(params, m)
        leads = leads_at_month(params, sessions)
        customers = customers_at_month(params, leads)
        revenue = revenue_at_month(params, customers)
        cost = cost_at_month(params, m)
        bl_value = backlink_value_at_month(params, m)

        cumulative_cost += cost
        cumulative_revenue += revenue
        cumulative_backlink_value += bl_value
        total_value = cumulative_revenue + cumulative_backlink_value
        cumulative_net = total_value - cumulative_cost

        rows.append({
            "month": m,
            "sessions": int(sessions),
            "leads": leads,
            "customers": customers,
            "revenue": revenue,
            "cost": round(cost, 2),
            "backlink_value": bl_value,
            "cumulative_cost": round(cumulative_cost, 2),
            "cumulative_revenue": round(cumulative_revenue, 2),
            "cumulative_backlink_value": round(cumulative_backlink_value, 2),
            "cumulative_net": round(cumulative_net, 2),
        })

    return rows
def find_break_even_month(projection):
    for row in projection:
        if row["cumulative_net"] >= 0:
            return row["month"]
    return None
def calculate_minimum_traffic(params):
    """
    What monthly traffic volume is needed to break even within 12 months?
    Solve for traffic where 12-month cumulative net >= 0.
    Uses binary search.
    """
    target_months = 12
    total_cost_12mo = params["build_cost"] + params["monthly_maintenance"] * target_months

    # Revenue per session (steady state, month 12)
    completion = params["tool_completion_rate"]
    lead_cap = params["lead_capture_rate"]
    trial = params["lead_to_trial_rate"]
    paid = params["trial_to_paid_rate"]
    ltv = params["ltv"]
    bl_monthly = params.get("backlink_value_monthly", 0)

    revenue_per_session = completion * lead_cap * trial * paid * ltv

    # Total sessions needed over 12 months (ignoring ramp for simplification)
    if revenue_per_session <= 0:
        return None

    # With backlink value: total_value = sessions_total × revenue_per_session + 12 × bl_monthly
    # sessions_total = total needed
    total_bl_value = bl_monthly * 12 * 0.5  # ramp factor
    needed_from_sessions = max(0, total_cost_12mo - total_bl_value)
    min_monthly_sessions = needed_from_sessions / (target_months * 0.6 * revenue_per_session)
    # 0.6 factor: first 3 months lower traffic during ramp

    return round(min_monthly_sessions, 0)

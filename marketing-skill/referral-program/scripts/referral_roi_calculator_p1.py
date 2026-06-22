# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from referral_roi_calculator_base import *  # noqa: F403,E402


def calculate_referrals_per_month(params):
    """How many successful referrals per month?"""
    active_users = params["active_users"]
    referral_rate = params["referral_rate"]
    referrals_per_referrer = params["referrals_per_referrer"]
    conversion_rate = params["referral_conversion_rate"]

    active_referrers = active_users * referral_rate
    referrals_sent = active_referrers * referrals_per_referrer
    conversions = referrals_sent * conversion_rate

    return {
        "active_referrers": round(active_referrers, 1),
        "referrals_sent": round(referrals_sent, 1),
        "new_customers_per_month": round(conversions, 1),
    }
def calculate_monthly_program_cost(params, new_customers_per_month):
    """Total cost of running the program for one month."""
    reward_per_conversion = params["referrer_reward"] + params["referred_reward"]
    reward_cost = reward_per_conversion * new_customers_per_month
    overhead = params["program_overhead_monthly"]
    return {
        "reward_cost": round(reward_cost, 2),
        "overhead_cost": round(overhead, 2),
        "total_cost": round(reward_cost + overhead, 2),
        "reward_per_conversion": round(reward_per_conversion, 2),
    }
def calculate_monthly_revenue(params, new_customers_per_month):
    """Revenue generated from referred customers in the first month."""
    # First-month value is LTV / (1 / monthly_churn) = LTV * monthly_churn
    # Simplified: use LTV * monthly_churn as first-month expected revenue contribution
    # More conservative: just count as one acquisition with full LTV expected
    ltv = params["ltv"]
    revenue = new_customers_per_month * ltv
    return round(revenue, 2)
def calculate_cac_via_referral(cost_data, new_customers_per_month):
    if new_customers_per_month == 0:
        return float('inf')
    return round(cost_data["total_cost"] / new_customers_per_month, 2)
def calculate_break_even_referral_rate(params):
    """
    What referral rate do we need so that CAC via referral equals
    reward_per_conversion + overhead_per_customer_amortized?
    
    We want: total_cost / new_customers = cac_target
    Solving for referral_rate where cac_target = 50% of paid CAC (our target)
    """
    target_cac = params["cac"] * 0.5  # goal: 50% of current CAC
    ltv = params["ltv"]
    active_users = params["active_users"]
    referrals_per_referrer = params["referrals_per_referrer"]
    conversion_rate = params["referral_conversion_rate"]
    reward_per_conversion = params["referrer_reward"] + params["referred_reward"]
    overhead = params["program_overhead_monthly"]

    # CAC_referral = (reward × conversions + overhead) / conversions
    #              = reward + overhead/conversions
    # Solve: target_cac = reward + overhead / (active_users × rate × referrals_per_referrer × conversion_rate)
    # conversions_needed = overhead / (target_cac - reward)

    if target_cac <= reward_per_conversion:
        return None  # impossible — reward alone exceeds target CAC

    conversions_needed = overhead / (target_cac - reward_per_conversion)
    referral_rate_needed = conversions_needed / (active_users * referrals_per_referrer * conversion_rate)

    return round(referral_rate_needed, 4)
def calculate_optimal_reward(params):
    """
    What's the maximum reward you can afford while keeping CAC via referral
    under 60% of paid CAC?
    
    max_total_reward = 0.60 × paid_CAC (using conversion-amortized overhead)
    """
    target_cac = params["cac"] * 0.60
    overhead_amortized = params["program_overhead_monthly"] / max(
        calculate_referrals_per_month(params)["new_customers_per_month"], 1
    )
    max_reward = target_cac - overhead_amortized

    # Split recommendation: 60% referrer, 40% referred (double-sided)
    referrer_portion = round(max_reward * 0.60, 2)
    referred_portion = round(max_reward * 0.40, 2)

    return {
        "max_total_reward": round(max(max_reward, 0), 2),
        "recommended_referrer_reward": max(referrer_portion, 0),
        "recommended_referred_reward": max(referred_portion, 0),
        "reward_as_pct_ltv": round((max_reward / params["ltv"]) * 100, 1) if params["ltv"] > 0 else 0,
    }
def calculate_roi(params):
    """
    Program ROI over the modeling period.
    ROI = (Revenue from referred customers - Program costs) / Program costs
    """
    months = params["months_to_model"]
    monthly = calculate_referrals_per_month(params)
    new_customers = monthly["new_customers_per_month"]
    costs = calculate_monthly_program_cost(params, new_customers)

    total_cost = costs["total_cost"] * months
    total_ltv_generated = new_customers * params["ltv"] * months
    net_benefit = total_ltv_generated - total_cost
    roi = (net_benefit / total_cost * 100) if total_cost > 0 else 0

    return {
        "total_cost": round(total_cost, 2),
        "total_ltv_generated": round(total_ltv_generated, 2),
        "net_benefit": round(net_benefit, 2),
        "roi_pct": round(roi, 1),
    }

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from referral_roi_calculator_base import *  # noqa: F403,E402
# fmt: off
from referral_roi_calculator_p1 import calculate_monthly_program_cost, calculate_referrals_per_month  # noqa: E402,E501
# fmt: on


def build_monthly_projection(params):
    """Build a month-by-month projection table."""
    months = params["months_to_model"]
    monthly = calculate_referrals_per_month(params)
    new_per_month = monthly["new_customers_per_month"]
    costs = calculate_monthly_program_cost(params, new_per_month)
    ltv = params["ltv"]

    rows = []
    cumulative_customers = 0
    cumulative_cost = 0
    cumulative_revenue = 0

    for m in range(1, months + 1):
        cumulative_customers += new_per_month
        month_cost = costs["total_cost"]
        month_revenue = new_per_month * ltv
        cumulative_cost += month_cost
        cumulative_revenue += month_revenue
        cumulative_net = cumulative_revenue - cumulative_cost

        rows.append({
            "month": m,
            "new_customers": round(new_per_month, 1),
            "cumulative_customers": round(cumulative_customers, 1),
            "monthly_cost": round(month_cost, 2),
            "cumulative_cost": round(cumulative_cost, 2),
            "monthly_ltv": round(month_revenue, 2),
            "cumulative_net": round(cumulative_net, 2),
        })

    return rows
def find_break_even_month(projection):
    for row in projection:
        if row["cumulative_net"] >= 0:
            return row["month"]
    return None
def format_currency(value):
    return f"${value:,.2f}"
def format_pct(value):
    return f"{value:.1f}%"
def print_report(params, results):
    monthly = results["monthly_referrals"]
    costs = results["monthly_costs"]
    cac = results["cac_via_referral"]
    roi = results["roi"]
    break_even_rate = results["break_even_referral_rate"]
    optimal_reward = results["optimal_reward"]
    projection = results["monthly_projection"]
    break_even_month = results["break_even_month"]

    paid_cac = params["cac"]
    ltv = params["ltv"]

    print("\n" + "=" * 60)
    print("REFERRAL PROGRAM ROI CALCULATOR")
    print("=" * 60)

    print("\n📊 INPUT PARAMETERS")
    print(f"  LTV per customer:           {format_currency(ltv)}")
    print(f"  Current paid CAC:           {format_currency(paid_cac)}")
    print(f"  Active users:               {params['active_users']:,}")
    print(f"  Referral rate (monthly):    {format_pct(params['referral_rate'] * 100)}")
    print(f"  Referrals per referrer:     {params['referrals_per_referrer']}")
    print(f"  Referral conversion rate:   {format_pct(params['referral_conversion_rate'] * 100)}")
    print(f"  Referrer reward:            {format_currency(params['referrer_reward'])}")
    print(f"  Referred user reward:       {format_currency(params['referred_reward'])}")
    print(f"  Program overhead/month:     {format_currency(params['program_overhead_monthly'])}")

    print("\n📈 MONTHLY PERFORMANCE (STEADY STATE)")
    print(f"  Active referrers/month:     {monthly['active_referrers']}")
    print(f"  Referrals sent/month:       {monthly['referrals_sent']}")
    print(f"  New customers/month:        {monthly['new_customers_per_month']}")
    print(f"  Monthly program cost:       {format_currency(costs['total_cost'])}")
    print(f"    ↳ Reward cost:            {format_currency(costs['reward_cost'])}")
    print(f"    ↳ Overhead:               {format_currency(costs['overhead_cost'])}")
    print(f"  CAC via referral:           {format_currency(cac)}")
    print(f"  Paid CAC:                   {format_currency(paid_cac)}")
    savings_pct = ((paid_cac - cac) / paid_cac * 100) if paid_cac > 0 else 0
    savings_label = f"{savings_pct:.0f}% cheaper than paid" if cac < paid_cac else "⚠️  More expensive than paid"
    print(f"  CAC comparison:             {savings_label}")

    print(f"\n💰 ROI OVER {params['months_to_model']} MONTHS")
    print(f"  Total program cost:         {format_currency(roi['total_cost'])}")
    print(f"  Total LTV generated:        {format_currency(roi['total_ltv_generated'])}")
    print(f"  Net benefit:                {format_currency(roi['net_benefit'])}")
    print(f"  Program ROI:                {format_pct(roi['roi_pct'])}")

    if break_even_month:
        print(f"  Break-even:                 Month {break_even_month}")
    else:
        print(f"  Break-even:                 Not reached in {params['months_to_model']} months")

    print("\n🎯 OPTIMIZATION INSIGHTS")
    if break_even_rate:
        current_rate = params["referral_rate"]
        rate_gap = break_even_rate - current_rate
        if rate_gap > 0:
            print(f"  Break-even referral rate:   {format_pct(break_even_rate * 100)} "
                  f"(you're at {format_pct(current_rate * 100)} — need +{format_pct(rate_gap * 100)})")
        else:
            print(f"  Break-even referral rate:   {format_pct(break_even_rate * 100)} ✅ Already above break-even")
    else:
        print(f"  Break-even referral rate:   ⚠️  Reward alone exceeds target CAC — reduce reward or increase LTV")

    print(f"\n  Optimal reward sizing (to keep CAC at ≤60% of paid CAC):")
    print(f"    Max total reward/referral:  {format_currency(optimal_reward['max_total_reward'])}")
    print(f"    Recommended referrer:       {format_currency(optimal_reward['recommended_referrer_reward'])}")
    print(f"    Recommended referred user:  {format_currency(optimal_reward['recommended_referred_reward'])}")
    print(f"    Reward as % of LTV:         {format_pct(optimal_reward['reward_as_pct_ltv'])}")

    current_total_reward = params["referrer_reward"] + params["referred_reward"]
    if current_total_reward > optimal_reward["max_total_reward"] and optimal_reward["max_total_reward"] > 0:
        print(f"  ⚠️  Your current reward ({format_currency(current_total_reward)}) "
              f"exceeds optimal ({format_currency(optimal_reward['max_total_reward'])})")
    elif optimal_reward["max_total_reward"] > 0:
        print(f"  ✅ Your current reward ({format_currency(current_total_reward)}) is within optimal range")

    print(f"\n📅 MONTHLY PROJECTION (first {min(6, len(projection))} months)")
    print(f"  {'Month':>5}  {'New Cust':>9}  {'Cumul Cust':>11}  {'Monthly Cost':>13}  {'Cumul Net':>11}")
    print(f"  {'-'*5}  {'-'*9}  {'-'*11}  {'-'*13}  {'-'*11}")
    for row in projection[:6]:
        net_str = format_currency(row["cumulative_net"])
        if row["cumulative_net"] < 0:
            net_str = f"({format_currency(abs(row['cumulative_net']))})"
        print(f"  {row['month']:>5}  {row['new_customers']:>9.1f}  {row['cumulative_customers']:>11.1f}  "
              f"{format_currency(row['monthly_cost']):>13}  {net_str:>11}")

    print("\n" + "=" * 60)

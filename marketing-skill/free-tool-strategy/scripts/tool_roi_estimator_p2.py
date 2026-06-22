# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_roi_estimator_base import *  # noqa: F403,E402


def calculate_roi_summary(projection, params):
    if not projection:
        return {}
    last = projection[-1]
    total_cost = last["cumulative_cost"]
    total_revenue = last["cumulative_revenue"]
    total_value = total_revenue + last["cumulative_backlink_value"]
    net = last["cumulative_net"]
    roi = (net / total_cost * 100) if total_cost > 0 else 0
    total_leads = sum(r["leads"] for r in projection)
    total_customers = sum(r["customers"] for r in projection)
    cost_per_lead = total_cost / total_leads if total_leads > 0 else 0

    return {
        "total_cost": round(total_cost, 2),
        "total_revenue": round(total_revenue, 2),
        "total_value_with_backlinks": round(total_value, 2),
        "net_benefit": round(net, 2),
        "roi_pct": round(roi, 1),
        "total_leads": round(total_leads, 0),
        "total_customers": round(total_customers, 1),
        "cost_per_lead": round(cost_per_lead, 2),
    }
def fc(value):
    return f"${value:,.2f}"
def fp(value):
    return f"{value:.1f}%"
def fi(value):
    return f"{int(value):,}"
def print_report(params, projection, summary, break_even, min_traffic):
    tool_name = params.get("tool_name", "Free Tool")
    months = params["months_to_model"]

    print("\n" + "=" * 65)
    print(f"FREE TOOL ROI ESTIMATOR — {tool_name.upper()}")
    print("=" * 65)

    print("\n📊 INPUT PARAMETERS")
    print(f"  Build cost (one-time):          {fc(params['build_cost'])}")
    print(f"  Monthly maintenance:            {fc(params['monthly_maintenance'])}")
    print(f"  Starting monthly traffic:       {fi(params['traffic_month_1'])} sessions")
    print(f"  Monthly traffic growth:         {fp(params['traffic_growth_rate'] * 100)}")
    print(f"  SEO ramp period:               {params.get('seo_ramp_months', 3)} months")
    print(f"  Tool completion rate:           {fp(params['tool_completion_rate'] * 100)}")
    print(f"  Lead capture rate:             {fp(params['lead_capture_rate'] * 100)} (of completions)")
    print(f"  Lead → trial rate:             {fp(params['lead_to_trial_rate'] * 100)}")
    print(f"  Trial → paid rate:             {fp(params['trial_to_paid_rate'] * 100)}")
    print(f"  LTV:                           {fc(params['ltv'])}")
    print(f"  Backlink value (monthly):      {fc(params.get('backlink_value_monthly', 0))}")

    print(f"\n📈 {months}-MONTH SUMMARY")
    print(f"  Total investment:               {fc(summary['total_cost'])}")
    print(f"  Revenue from leads:             {fc(summary['total_revenue'])}")
    print(f"  Backlink value:                 {fc(summary.get('total_value_with_backlinks', 0) - summary['total_revenue'])}")
    print(f"  Total value generated:          {fc(summary.get('total_value_with_backlinks', summary['total_revenue']))}")
    print(f"  Net benefit:                    {fc(summary['net_benefit'])}")
    print(f"  ROI:                            {fp(summary['roi_pct'])}")

    print(f"\n🎯 LEAD & CUSTOMER METRICS")
    print(f"  Total leads generated:          {fi(summary['total_leads'])}")
    print(f"  Total customers acquired:       {round(summary['total_customers'], 1)}")
    print(f"  Cost per lead:                  {fc(summary['cost_per_lead'])}")
    print(f"  CAC via tool:                   {fc(summary['total_cost'] / max(summary['total_customers'], 0.01))}")

    print(f"\n⏱  BREAK-EVEN ANALYSIS")
    if break_even:
        print(f"  Break-even month:               Month {break_even}")
        assessment = "🟢 Fast payback" if break_even <= 6 else "🟡 Moderate" if break_even <= 12 else "🔴 Long payback"
        print(f"  Assessment:                     {assessment}")
    else:
        print(f"  Break-even month:               Not reached in {months} months ⚠️")
        print(f"  Action needed: Increase traffic, improve completion/capture rate, or reduce build cost")

    if min_traffic:
        print(f"  Min traffic for 12-mo break-even: {fi(min_traffic)} sessions/month")
        current = params["traffic_month_1"]
        if current >= min_traffic:
            print(f"  Your projected traffic ({fi(current)}/mo) exceeds minimum ✅")
        else:
            gap = min_traffic - current
            print(f"  Traffic gap: need {fi(gap)} more sessions/month than projected ⚠️")

    print(f"\n📅 MONTHLY PROJECTION")
    print(f"  {'Mo':>3}  {'Sessions':>9}  {'Leads':>6}  {'Custs':>6}  {'Revenue':>9}  {'Cum Net':>10}")
    print(f"  {'-'*3}  {'-'*9}  {'-'*6}  {'-'*6}  {'-'*9}  {'-'*10}")
    for row in projection:
        net = row["cumulative_net"]
        net_str = fc(net) if net >= 0 else f"({fc(abs(net))})"
        be_marker = " ← break-even" if row["month"] == break_even else ""
        print(f"  {row['month']:>3}  {fi(row['sessions']):>9}  {row['leads']:>6.1f}  {row['customers']:>6.2f}"
              f"  {fc(row['revenue']):>9}  {net_str:>10}{be_marker}")

    print("\n" + "=" * 65)

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    roi = summary["roi_pct"]
    if roi > 200:
        print("  ✅ Strong ROI case — build it, invest in distribution")
    elif roi > 50:
        print("  🟡 Positive ROI but slim — validate keyword volume before committing full build cost")
        print("     Consider: MVP version (no-code) to test demand before full dev investment")
    else:
        print("  🔴 ROI case is weak — investigate:")
        print("     1. Is the target keyword validated? (check search volume)")
        print("     2. Can you reduce build cost? (no-code MVP first)")
        print("     3. Is the lead-to-customer conversion realistic?")
        print("     4. Is the LTV accurate?")

    completion = params["tool_completion_rate"]
    if completion < 0.40:
        print("  ⚠️  Low completion rate — reconsider UX or number of required inputs")
    if params["lead_capture_rate"] < 0.05:
        print("  ⚠️  Low lead capture — check gate placement (should be after value is delivered)")
    if break_even and break_even > 18:
        print("  ⚠️  Long break-even — prioritize launch distribution to accelerate traffic ramp")

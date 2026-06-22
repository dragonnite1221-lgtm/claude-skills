# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pricing_modeler_base import *  # noqa: F403,E402


def print_report(result, inputs):
    cur = result["current_state"]
    elast = result["elasticity"]
    tiers = result["tier_recommendation"]
    scenarios = result["price_scenarios"]

    print("\n" + "="*65)
    print("  PRICING MODELER")
    print("="*65)

    print(f"\n📊 CURRENT STATE")
    print(f"   MRR:                     ${cur['current_mrr']:,.0f}")
    print(f"   Customers:               {cur['customers']}")
    print(f"   ARPU:                    ${cur['arpu']:.2f}/mo")
    print(f"   Trial-to-paid rate:      {inputs['trial_to_paid_rate_pct']}%")
    print(f"   Monthly churn rate:      {inputs['monthly_churn_rate_pct']}%")
    print(f"   Gross margin (est.):     {cur['gross_margin_pct']:.1f}%")

    print(f"\n💡 PRICE ELASTICITY SIGNAL")
    print(f"   Signal:    {elast['signal'].replace('-', ' ').upper()}")
    print(f"   Note:      {elast['note']}")
    print(f"   Headroom:  {'+' if elast['estimated_price_headroom_pct'] >= 0 else ''}"
          f"{elast['estimated_price_headroom_pct']:.0f}%")
    print(f"   Test at:   ${elast['suggested_test_price']:.2f}/mo ARPU")

    print(f"\n📐 RECOMMENDED TIER STRUCTURE")
    tier_rat = tiers['rationale']
    print(f"   Market position:  {tier_rat['pricing_vs_market'].replace('-', ' ').title()}")
    print(f"   Competitor range: {tier_rat['competitor_range']}")
    print(f"   Min viable price: ${tier_rat['min_viable_price']:.2f}/mo")
    print(f"\n   ┌─────────────────┬────────────┬────────────────────────────────────┐")
    print(f"   │ Tier            │ Price      │ Positioning                        │")
    print(f"   ├─────────────────┼────────────┼────────────────────────────────────┤")
    for key in ["entry", "mid", "premium"]:
        t = tiers[key]
        name = t["name"].ljust(15)
        price = f"${t['recommended_price']}/mo".ljust(10)
        pos = t["positioning"][:34].ljust(34)
        print(f"   │ {name} │ {price} │ {pos} │")
    print(f"   └─────────────────┴────────────┴────────────────────────────────────┘")

    print(f"\n📈 REVENUE SCENARIOS (12-month projection)")
    print(f"   {'Scenario':<25} {'Mo 1 MRR':>10} {'Mo 6 MRR':>10} {'Mo 12 MRR':>10} {'12mo Total':>12}")
    print(f"   {'-'*67}")
    for s in scenarios:
        print(f"   {s['scenario']:<25} "
              f"${s['month_1_mrr']:>9,.0f} "
              f"${s['month_6_mrr']:>9,.0f} "
              f"${s['month_12_mrr']:>9,.0f} "
              f"${s['total_12mo_revenue']:>11,.0f}")

    print(f"\n🎯 RECOMMENDATION")
    best = max(scenarios, key=lambda s: s['total_12mo_revenue'])
    current = next((s for s in scenarios if s['scenario'] == 'Current pricing'), scenarios[0])
    uplift = best['total_12mo_revenue'] - current['total_12mo_revenue']
    print(f"   Best scenario:    {best['scenario']}")
    print(f"   12-month uplift:  ${uplift:,.0f} vs. current")
    print(f"   Note: Projections assume trial volume and churn hold constant.")
    print(f"         Test price increases on new customers first.")

    print("\n" + "="*65 + "\n")

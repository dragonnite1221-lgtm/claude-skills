# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from marketing_budget_modeler_base import *  # noqa: F403,E402
# fmt: off
from marketing_budget_modeler_p1 import ARPU_MONTHLY, ASP_ANNUAL, CHANNELS, Channel, FUNNEL, GROSS_MARGIN, LTV, ScenarioResult, TARGET_NEW_ARR, customers_needed, ltv_to_cac, mqls_needed_total, score_channel  # noqa: E402,E501
from marketing_budget_modeler_p2 import build_scenario, fmt_currency, fmt_ratio, print_channel_table, print_funnel_summary, print_header  # noqa: E402,E501
# fmt: on


def print_scenario(result: ScenarioResult, channels: List[Channel]) -> None:
    print_header(f"Scenario: {result.name}")
    print(f"  Total marketing budget:  {fmt_currency(result.total_budget)}")
    print(f"  Projected customers:     {result.projected_customers}")
    print(f"  Projected new ARR:       {fmt_currency(result.projected_arr)}")
    print(f"  Blended CAC:             {fmt_currency(result.blended_cac)}")
    blended_ltv_cac = LTV / result.blended_cac if result.blended_cac > 0 else 0
    blended_payback = result.blended_cac / (ARPU_MONTHLY * GROSS_MARGIN)
    print(f"  Blended LTV:CAC:         {fmt_ratio(blended_ltv_cac)}", end="")
    if blended_ltv_cac < 1:
        print("  ⚠ BELOW BREAK-EVEN")
    elif blended_ltv_cac < 3:
        print("  △ MARGINAL")
    elif blended_ltv_cac >= 3:
        print("  ✓ HEALTHY")
    else:
        print()
    print(f"  Blended payback:         {blended_payback:.1f} months")
    if result.notes:
        print(f"\n  Notes:")
        for note in result.notes:
            print(f"    • {note}")

    print(f"\n  {'Channel':<25} {'MQLs':>6} {'Budget':>10} {'% of Budget':>12} {'LTV:CAC':>8}")
    print("  " + "-" * 65)
    for ch in sorted(channels, key=score_channel, reverse=True):
        mqls = result.channel_mqls.get(ch.name, 0)
        budget = result.channel_budgets.get(ch.name, 0.0)
        pct = (budget / result.total_budget * 100) if result.total_budget > 0 else 0
        ratio = ltv_to_cac(ch.ltv, ch.cac)
        print(
            f"  {ch.name:<25} {mqls:>6} {fmt_currency(budget):>10} "
            f"{pct:>11.1f}% {fmt_ratio(ratio):>8}"
        )
def print_scenario_comparison(scenarios: List[ScenarioResult]) -> None:
    print_header("Scenario Comparison")
    header = f"{'Scenario':<18} {'Budget':>10} {'Customers':>10} {'ARR':>10} {'Blended CAC':>12} {'LTV:CAC':>8} {'Payback':>9}"
    print(header)
    print("-" * 82)
    for s in scenarios:
        blended_ltv_cac = LTV / s.blended_cac if s.blended_cac > 0 else 0
        blended_payback = s.blended_cac / (ARPU_MONTHLY * GROSS_MARGIN)
        print(
            f"{s.name:<18} {fmt_currency(s.total_budget):>10} "
            f"{s.projected_customers:>10} {fmt_currency(s.projected_arr):>10} "
            f"{fmt_currency(s.blended_cac):>12} {fmt_ratio(blended_ltv_cac):>8} "
            f"{blended_payback:>7.1f}mo"
        )
def print_recommendations(channels: List[Channel]) -> None:
    print_header("Channel Recommendations")
    scale = [ch for ch in channels if score_channel(ch) >= 1.5 and ch.trend in ("improving", "stable")]
    hold = [ch for ch in channels if 0.8 <= score_channel(ch) < 1.5 or (ch.trend == "stable" and ltv_to_cac(ch.ltv, ch.cac) >= 3)]
    cut = [ch for ch in channels if ltv_to_cac(ch.ltv, ch.cac) < 2 or ch.trend == "declining"]
    # Deduplicate
    hold = [ch for ch in hold if ch not in scale]
    cut = [ch for ch in cut if ch not in scale and ch not in hold]

    if scale:
        print("  SCALE (strong LTV:CAC, improving or stable trend):")
        for ch in scale:
            print(f"    + {ch.name}  [LTV:CAC {fmt_ratio(ltv_to_cac(ch.ltv, ch.cac))}, payback {ch.payback_months:.0f}mo]")
    if hold:
        print("  HOLD (monitor — adequate but not outstanding):")
        for ch in hold:
            print(f"    = {ch.name}  [LTV:CAC {fmt_ratio(ltv_to_cac(ch.ltv, ch.cac))}, trend: {ch.trend}]")
    if cut:
        print("  CUT or REDUCE (poor LTV:CAC or declining):")
        for ch in cut:
            print(f"    - {ch.name}  [LTV:CAC {fmt_ratio(ltv_to_cac(ch.ltv, ch.cac))}, trend: {ch.trend}]")
def main() -> None:
    customers = customers_needed(TARGET_NEW_ARR, ASP_ANNUAL)
    total_mqls = mqls_needed_total(customers, FUNNEL.mql_to_close)

    print_channel_table(CHANNELS)
    print_funnel_summary(customers, total_mqls)

    scenarios = [
        build_scenario(
            name="Conservative",
            channels=CHANNELS,
            total_mqls=total_mqls,
            multiplier=0.7,
            notes=[
                "Prioritizes lowest CAC channels only.",
                "May not reach MQL target — expect ~70% of goal.",
                "Best for capital-constrained orgs or short runway.",
            ],
        ),
        build_scenario(
            name="Moderate",
            channels=CHANNELS,
            total_mqls=total_mqls,
            multiplier=1.0,
            notes=[
                "Balanced allocation — efficiency-first but full MQL target.",
                "Recommended baseline. Revisit Q2 based on actuals.",
            ],
        ),
        build_scenario(
            name="Aggressive",
            channels=CHANNELS,
            total_mqls=total_mqls,
            multiplier=1.4,
            notes=[
                "Pushes all channels toward capacity ceiling.",
                "Higher spend on lower-efficiency channels to hit volume.",
                "Requires > 18-month runway to justify payback period.",
            ],
        ),
    ]

    for scenario in scenarios:
        print_scenario(scenario, CHANNELS)

    print_scenario_comparison(scenarios)
    print_recommendations(CHANNELS)

    print("\n" + "=" * 72)
    print("  Key questions before finalizing budget:")
    print("    1. What is the payback period the CFO/board will accept?")
    print("    2. Is CAC for declining-trend channels actually recoverable?")
    print("    3. Does the moderate scenario require sales headcount increase?")
    print("    4. Which channels have capacity to absorb 20% more spend?")
    print("=" * 72 + "\n")

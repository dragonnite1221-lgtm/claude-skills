# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scenario_modeler_base import *  # noqa: F403,E402
# fmt: off
from scenario_modeler_p1 import Scenario, Severity, calculate_impact  # noqa: E402,E501
from scenario_modeler_p2 import format_currency, identify_triggers  # noqa: E402,E501
# fmt: on


def print_report(scenario: Scenario) -> None:
    """Print full scenario analysis report."""
    print("\n" + "=" * 70)
    print(f"SCENARIO WAR ROOM: {scenario.name.upper()}")
    print("=" * 70)

    # Baseline
    print(f"\n📊 BASELINE")
    print(f"   Current ARR:    {format_currency(scenario.current_arr_usd)}")
    print(f"   Monthly Burn:   {format_currency(scenario.monthly_burn_usd)}")
    print(f"   Runway:         {scenario.current_runway_months} months")

    # Variables
    print(f"\n⚡ SCENARIO VARIABLES ({len(scenario.variables)})")
    for i, var in enumerate(scenario.variables, 1):
        prob_pct = int(var.probability * 100)
        print(f"\n  Variable {i}: {var.name}")
        print(f"    {var.description}")
        print(f"    Probability: {prob_pct}%  |  Timeline: {var.timeline_days} days")
        print(f"    ARR impact: -{var.arrt_impact_pct}%  |  "
              f"Runway impact: -{var.runway_impact_months} months")
        print(f"    Affected: {', '.join(d.value for d in var.affected_domains)}")

    # Combined probability
    combined_prob = 1.0
    for var in scenario.variables:
        combined_prob *= var.probability
    print(f"\n  Combined probability (all hit): {combined_prob * 100:.1f}%")

    # Severity Levels
    print(f"\n{'=' * 70}")
    print("SEVERITY ANALYSIS")
    print("=" * 70)

    for severity in Severity:
        if severity == Severity.BASE and len(scenario.variables) < 1:
            continue
        if severity == Severity.STRESS and len(scenario.variables) < 2:
            continue

        impact = calculate_impact(scenario, severity)

        icon = {"base": "🟡", "stress": "🔴", "severe": "💀"}[impact["severity"]]
        print(f"\n{icon} {impact['severity'].upper()} SCENARIO")
        print(f"   Variables: {', '.join(impact['active_variables'])}")
        print(f"   ARR at risk: {format_currency(impact['arr_at_risk_usd'])} "
              f"({impact['arr_at_risk_pct']}%)")
        print(f"   Projected ARR: {format_currency(impact['projected_arr_usd'])}")
        print(f"   Runway: {impact['runway_months']} months "
              f"({impact['runway_change']:+.1f} months)")
        print(f"   Burn multiple: {impact['new_burn_multiple']}x")
        if impact['cascade_multiplier'] > 1.0:
            print(f"   Cascade amplifier: {impact['cascade_multiplier']}x "
                  f"(domains interact)")
        print(f"   Board escalation: {'⚠️  YES' if impact['board_escalation_required'] else 'No'}")
        print(f"   Existential risk: {'🚨 YES' if impact['existential_risk'] else 'No'}")

    # Cascade Map
    if scenario.cascades:
        print(f"\n{'=' * 70}")
        print("CASCADE MAP")
        print("=" * 70)
        for i, cascade in enumerate(scenario.cascades, 1):
            print(f"\n  [{i}] {cascade.trigger_domain.value}")
            print(f"       ↓ {cascade.mechanism}")
            print(f"       → {cascade.caused_domain.value} "
                  f"(amplified {cascade.severity_multiplier}x)")

    # Early Warning Triggers
    print(f"\n{'=' * 70}")
    print("EARLY WARNING TRIGGERS")
    print("=" * 70)
    triggers = identify_triggers(scenario.variables)
    for trigger in triggers:
        print(f"\n  📡 {trigger['variable']}")
        print(f"     Watch: {trigger['timeline']}")
        print(f"     Owner: {trigger['response_owner']}")
        for signal in trigger['signals']:
            print(f"     • {signal}")

    # Hedges
    if scenario.hedges:
        print(f"\n{'=' * 70}")
        print("HEDGING STRATEGIES (act now)")
        print("=" * 70)
        sorted_hedges = sorted(scenario.hedges,
                               key=lambda h: h.reduces_probability, reverse=True)
        for hedge in sorted_hedges:
            print(f"\n  ✅ {hedge.action}")
            print(f"     Cost: {format_currency(hedge.cost_usd)}/year  |  "
                  f"Owner: {hedge.owner}  |  Deadline: {hedge.deadline_days} days")
            print(f"     Impact: {hedge.impact_description}")
            print(f"     Risk reduction: {int(hedge.reduces_probability * 100)}%")

    print(f"\n{'=' * 70}\n")

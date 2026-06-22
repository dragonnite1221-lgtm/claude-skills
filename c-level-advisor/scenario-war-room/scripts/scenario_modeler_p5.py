# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scenario_modeler_base import *  # noqa: F403,E402
# fmt: off
from scenario_modeler_p1 import Domain, Scenario, Severity, Variable, calculate_impact  # noqa: E402,E501
from scenario_modeler_p3 import print_report  # noqa: E402,E501
from scenario_modeler_p4 import build_sample_scenario  # noqa: E402,E501
# fmt: on


def interactive_mode() -> Scenario:
    """Simple CLI for building a custom scenario."""
    print("\n🔴 SCENARIO WAR ROOM — Custom Scenario Builder")
    print("=" * 50)
    print("Define up to 3 scenario variables.\n")

    name = input("Scenario name: ").strip() or "Custom Scenario"

    current_arr = int(input("Current ARR ($): ").strip() or "2000000")
    current_runway = int(input("Current runway (months): ").strip() or "14")
    monthly_burn = int(current_arr / current_runway) if current_runway > 0 else 140000

    variables = []
    for i in range(1, 4):
        print(f"\nVariable {i} (press Enter to skip):")
        var_name = input("  Name: ").strip()
        if not var_name:
            break

        desc = input("  Description: ").strip() or var_name
        prob = float(input("  Probability (0-100%): ").strip() or "20") / 100
        arr_impact = float(input("  ARR impact (%): ").strip() or "10")
        runway_impact = float(input("  Runway impact (months): ").strip() or "2")
        timeline = int(input("  Timeline (days): ").strip() or "90")

        variables.append(Variable(
            name=var_name,
            description=desc,
            probability=prob,
            arrt_impact_pct=arr_impact,
            runway_impact_months=runway_impact,
            affected_domains=[Domain.FINANCIAL, Domain.REVENUE],
            timeline_days=timeline,
        ))

    if not variables:
        print("No variables defined. Using sample scenario.")
        return build_sample_scenario()

    return Scenario(
        name=name,
        variables=variables,
        cascades=[],
        hedges=[],
        current_arr_usd=current_arr,
        current_runway_months=current_runway,
        monthly_burn_usd=monthly_burn,
    )
def main():
    print("\n🔴 SCENARIO WAR ROOM")
    print("Multi-variable cascade modeler for startup adversity planning\n")

    if "--interactive" in sys.argv or "-i" in sys.argv:
        scenario = interactive_mode()
    else:
        print("Running sample scenario: Customer Churn + Fundraise Miss + Eng Attrition")
        print("(Use --interactive or -i for custom scenario)\n")
        scenario = build_sample_scenario()

    print_report(scenario)

    if "--json" in sys.argv:
        results = {}
        for severity in Severity:
            impact = calculate_impact(scenario, severity)
            results[severity.value] = impact
        print(json.dumps(results, indent=2))

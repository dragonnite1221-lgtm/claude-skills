# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tracking_plan_generator_base import *  # noqa: F403,E402
# fmt: off
from tracking_plan_generator_p1 import SAMPLE_INPUT  # noqa: E402,E501
from tracking_plan_generator_p3 import generate_tracking_plan  # noqa: E402,E501
# fmt: on


def print_report(result, inputs):
    print("\n" + "="*65)
    print("  TRACKING PLAN GENERATOR")
    print("="*65)

    print(f"\n📋 BUSINESS TYPE: {inputs.get('business_type', 'saas').upper()}")

    events = result["event_taxonomy"]
    by_priority = defaultdict(list)
    for ev in events:
        by_priority[ev["priority"]].append(ev)

    print(f"\n📊 EVENT TAXONOMY ({len(events)} events)")
    for priority in ["critical", "high", "medium", "low"]:
        evs = by_priority.get(priority, [])
        if evs:
            marker = "🔴" if priority == "critical" else "🟡" if priority == "high" else "⚪"
            print(f"\n  {marker} {priority.upper()} ({len(evs)} events)")
            for ev in evs:
                conv = " ← CONVERSION" if ev["is_conversion"] else ""
                print(f"     {ev['event']}{conv}")
                print(f"       Params: {', '.join(ev['parameters'][:4])}" +
                      (f"... +{len(ev['parameters'])-4} more" if len(ev['parameters']) > 4 else ""))

    conversions = result["conversion_events"]
    print(f"\n🎯 CONVERSION EVENTS ({len(conversions)})")
    for ev in conversions:
        print(f"   • {ev}")

    dims = result["ga4_custom_dimensions"]
    print(f"\n📐 CUSTOM DIMENSIONS")
    print(f"   User-scoped ({len(dims['user_scoped'])}): " +
          ", ".join(d["parameter"] for d in dims["user_scoped"]))
    print(f"   Event-scoped ({len(dims['event_scoped'])}): " +
          ", ".join(d["parameter"] for d in dims["event_scoped"]))

    gtm = result["gtm_configuration"]
    print(f"\n🏷️  GTM CONFIGURATION")
    print(f"   Tags to create:     {len(gtm['tags'])}")
    print(f"   Triggers to create: {gtm['trigger_count']}")
    print(f"   Variables to create:{gtm['variable_count']}")

    if result["consent_mode"]:
        print(f"\n🔒 CONSENT MODE: Advanced (required)")
        print(f"   Default state: analytics_storage=denied, ad_storage=denied")

    print(f"\n📋 IMPLEMENTATION ORDER")
    for step in result["implementation_order"]:
        print(f"   {step}")

    print("\n" + "="*65)
    print("  Run with --json flag to output full config as JSON")
    print("="*65 + "\n")
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Tracking plan generator — produces event taxonomy, GTM config, and GA4 dimension recommendations."
    )
    parser.add_argument(
        "input_file", nargs="?", default=None,
        help="JSON file with business config (default: run with sample SaaS data)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output full config as JSON"
    )
    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file) as f:
            inputs = json.load(f)
    else:
        if not args.json:
            print("No input file provided. Running with sample data...\n")
        inputs = SAMPLE_INPUT

    result = generate_tracking_plan(inputs)
    print_report(result, inputs)

    if args.json:
        print(json.dumps(result, indent=2))

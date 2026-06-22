# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from engagement_planner_base import *  # noqa: F403,E402
# fmt: off
from engagement_planner_p1 import list_techniques  # noqa: E402,E501
from engagement_planner_p2 import build_engagement_plan  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Red Team Engagement Planner — Builds structured engagement plans from MITRE ATT&CK techniques.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 engagement_planner.py --techniques T1059,T1078,T1003 --access-level external --authorized --json\n"
            "  python3 engagement_planner.py --techniques T1059,T1078 --crown-jewels 'DB,AD' --access-level credentialed --authorized --json\n"
            "  python3 engagement_planner.py --list-techniques\n"
            "\nExit codes:\n"
            "  0  Engagement plan generated successfully\n"
            "  1  Missing authorization or invalid input\n"
            "  2  Scope violation or technique outside access-level constraints"
        ),
    )
    parser.add_argument(
        "--techniques",
        type=str,
        default="",
        help="Comma-separated MITRE ATT&CK technique IDs (e.g. T1059,T1078,T1003)",
    )
    parser.add_argument(
        "--access-level",
        choices=["external", "internal", "credentialed"],
        default="external",
        help="Attacker access level for this engagement (default: external)",
    )
    parser.add_argument(
        "--crown-jewels",
        type=str,
        default="",
        help="Comma-separated crown jewel asset labels (e.g. 'DB,AD,PaymentSystem')",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=1,
        help="Number of target systems/segments (affects duration estimate, default: 1)",
    )
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Confirms signed RoE and executive authorization have been obtained",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--list-techniques",
        action="store_true",
        help="Print all available MITRE techniques and exit",
    )

    args = parser.parse_args()

    if args.list_techniques:
        list_techniques()  # exits internally

    # Authorization gate
    if not args.authorized:
        msg = (
            "Authorization required: obtain signed RoE before planning. "
            "Use --authorized flag only after legal sign-off."
        )
        if args.output_json:
            print(json.dumps({"error": msg, "exit_code": 1}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    if not args.techniques.strip():
        msg = "No techniques specified. Use --techniques T1059,T1078,... or --list-techniques."
        if args.output_json:
            print(json.dumps({"error": msg, "exit_code": 1}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    techniques_input = [t.strip() for t in args.techniques.split(",") if t.strip()]
    crown_jewels = [c.strip() for c in args.crown_jewels.split(",") if c.strip()]

    plan, violation_count = build_engagement_plan(
        techniques_input=techniques_input,
        access_level=args.access_level,
        crown_jewels=crown_jewels,
        target_count=args.target_count,
    )

    if args.output_json:
        print(json.dumps(plan, indent=2))
    else:
        summary = plan["engagement_summary"]
        print("\n=== RED TEAM ENGAGEMENT PLAN ===")
        print(f"Access Level    : {summary['access_level']}")
        print(f"Crown Jewels    : {', '.join(crown_jewels) if crown_jewels else 'Not specified'}")
        print(f"Techniques      : {summary['techniques_valid']}/{summary['techniques_requested']} valid")
        print(f"Est. Duration   : {summary['estimated_duration_days']} days")
        if summary["techniques_not_found"]:
            print(f"Not Found       : {', '.join(summary['techniques_not_found'])}")

        print("\n--- Kill-Chain Phases ---")
        for phase in plan["phases"]:
            print(f"\n  [{phase['phase'].upper()}]")
            for t in phase["techniques"]:
                print(f"    {t['id']:<12} {t['name']:<45} risk={t['detection_risk']:.2f}  effort={t['effort_score']:.3f}")

        print("\n--- Choke Points ---")
        if plan["choke_points"]:
            for cp in plan["choke_points"]:
                print(f"  {cp['technique_id']} {cp['technique_name']} — {cp['note']}")
        else:
            print("  None identified.")

        print("\n--- OPSEC Risks ---")
        for risk in plan["opsec_risks"]:
            print(f"  [{risk['severity'].upper()}] {risk['risk']}")
            print(f"    Mitigation: {risk['mitigation']}")

        if plan["scope_violations"]:
            print("\n--- SCOPE VIOLATIONS ---")
            for sv in plan["scope_violations"]:
                print(f"  {sv['technique_id']}: {sv['reason']}")

        print("\n--- Required Authorizations ---")
        for auth in plan["required_authorizations"]:
            print(f"  - {auth}")
        print()

    if violation_count > 0:
        sys.exit(2)
    sys.exit(0)

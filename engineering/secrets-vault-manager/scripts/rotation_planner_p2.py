# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rotation_planner_base import *  # noqa: F403,E402
# fmt: off
from rotation_planner_p1 import POLICY_DAYS, compute_schedule, load_inventory  # noqa: E402,E501
# fmt: on


def build_summary(schedule):
    """Build summary statistics."""
    total = len(schedule)
    by_urgency = {}
    by_type = {}
    by_owner = {}

    for entry in schedule:
        urg = entry["urgency"]
        by_urgency[urg] = by_urgency.get(urg, 0) + 1
        t = entry["type"]
        by_type[t] = by_type.get(t, 0) + 1
        o = entry["owner"]
        by_owner[o] = by_owner.get(o, 0) + 1

    return {
        "total_secrets": total,
        "by_urgency": by_urgency,
        "by_type": by_type,
        "by_owner": by_owner,
        "overdue_count": by_urgency.get("CRITICAL", 0),
        "due_within_7d": by_urgency.get("HIGH", 0),
    }
def print_human(schedule, summary, policy):
    """Print human-readable rotation plan."""
    print(f"=== Secret Rotation Plan (Policy: {policy}) ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total secrets: {summary['total_secrets']}")
    print()

    print("--- Urgency Summary ---")
    for urg in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = summary["by_urgency"].get(urg, 0)
        if count > 0:
            print(f"  {urg:10s}  {count}")
    print()

    if not schedule:
        print("No secrets in inventory.")
        return

    print("--- Rotation Schedule ---")
    print(f"  {'Name':30s}  {'Type':15s}  {'Urgency':10s}  {'Last Rotated':12s}  {'Next Due':12s}  {'Owner'}")
    print(f"  {'-'*30}  {'-'*15}  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*15}")

    for entry in schedule:
        overdue_marker = " **OVERDUE**" if entry["urgency"] == "CRITICAL" else ""
        print(
            f"  {entry['name']:30s}  {entry['type']:15s}  {entry['urgency']:10s}  "
            f"{entry['last_rotated']:12s}  {entry['next_rotation']:12s}  "
            f"{entry['owner']}{overdue_marker}"
        )

    print()
    print("--- Action Items ---")
    critical = [e for e in schedule if e["urgency"] == "CRITICAL"]
    high = [e for e in schedule if e["urgency"] == "HIGH"]

    if critical:
        print(f"  IMMEDIATE: Rotate {len(critical)} overdue secret(s):")
        for e in critical:
            print(f"    - {e['name']} ({e['type']}, owner: {e['owner']})")
    if high:
        print(f"  THIS WEEK: Rotate {len(high)} secret(s) due within 7 days:")
        for e in high:
            print(f"    - {e['name']} (due: {e['next_rotation']}, owner: {e['owner']})")
    if not critical and not high:
        print("  No urgent rotations needed.")
def main():
    parser = argparse.ArgumentParser(
        description="Create rotation schedule from a secret inventory file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Policies:
              30d   Aggressive — all secrets rotate within 30 days max
              60d   Standard — 60-day maximum rotation window
              90d   Relaxed — 90-day maximum rotation window

            Note: Some secret types (e.g., database passwords) have shorter
            built-in defaults that override the policy maximum.

            Example inventory file (secrets.json):
            [
              {"name": "prod-db", "type": "database", "store": "vault",
               "last_rotated": "2026-01-15", "owner": "platform-team",
               "environment": "production"}
            ]
        """),
    )
    parser.add_argument("--inventory", required=True, help="Path to JSON inventory file")
    parser.add_argument(
        "--policy",
        required=True,
        choices=["30d", "60d", "90d"],
        help="Rotation policy (maximum rotation interval)",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    policy_days = POLICY_DAYS[args.policy]
    inventory = load_inventory(args.inventory)
    schedule = compute_schedule(inventory, policy_days)
    summary = build_summary(schedule)

    result = {
        "policy": args.policy,
        "policy_days": policy_days,
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "schedule": schedule,
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print_human(schedule, summary, args.policy)

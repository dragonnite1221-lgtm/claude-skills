# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import FRAMEWORKS  # noqa: E402,E501
from compliance_tracker_p5 import estimate_roadmap, find_high_leverage_controls, fmt_dollars  # noqa: E402,E501
# fmt: on


def print_high_leverage(controls: list[dict]):
    hl = find_high_leverage_controls(controls)
    print(f"\n🎯 HIGH-LEVERAGE CONTROLS — Implement Once, Satisfy Multiple Frameworks")
    print("-" * 70)
    print(f"{'Control':<30} {'Frameworks':<35} {'Effort':<8} {'Cost'}")
    print("-" * 70)
    for c in hl:
        fw_list = " + ".join(FRAMEWORKS[fw]["name"] for fw in c["frameworks_applicable"])
        print(
            f"{c['name'][:29]:<30} {fw_list[:34]:<35} "
            f"{c['effort_days']:>3}d    {fmt_dollars(c['cost_usd'])}"
        )
def print_roadmap(controls: list[dict], target_frameworks: list[str]):
    ordered = estimate_roadmap(controls, target_frameworks)
    fw_names = " + ".join(FRAMEWORKS[fw]["name"] for fw in target_frameworks)
    print(f"\n🗺️  IMPLEMENTATION ROADMAP — {fw_names}")
    print("-" * 80)
    print("Priority order: most framework coverage first, then quick wins")
    print()

    cumulative_days = 0
    cumulative_cost = 0
    for i, c in enumerate(ordered, 1):
        cumulative_days += c["effort_days"]
        cumulative_cost += c["cost_usd"]
        fw_badges = ", ".join(
            FRAMEWORKS[fw]["name"] for fw in target_frameworks
            if fw in c["frameworks_applicable"]
        )
        print(f"  {i:>2}. {c['name']}")
        print(f"      Frameworks: {fw_badges}")
        print(f"      Effort: {c['effort_days']} days | Cost: {fmt_dollars(c['cost_usd'])} "
              f"| Cumulative: {cumulative_days}d / {fmt_dollars(cumulative_cost)}")
        if c.get("owner"):
            print(f"      Owner: {c['owner']}")
        print()
def print_framework_profiles():
    print("\n💼 FRAMEWORK PROFILES")
    print("-" * 70)
    for fw_id, fw in FRAMEWORKS.items():
        print(f"\n  {fw['name']} ({fw_id.upper()})")
        print(f"  Timeline:     ~{fw['typical_timeline_months']} months")
        print(f"  First-year cost: {fmt_dollars(fw['typical_cost_usd'])}")
        print(f"  Annual maintenance: {fmt_dollars(fw['annual_maintenance_usd'])}/yr")
        print(f"  Business value: {fw['business_value']}")
        print(f"  Required for:  {', '.join(fw['mandatory_for'])}")
def export_csv(controls: list[dict], filepath: str):
    fields = [
        "domain_id", "name", "frameworks_applicable", "framework_count",
        "effort_days", "cost_usd", "status", "owner", "target_date",
        "soc2_ref", "iso27001_ref", "hipaa_ref", "gdpr_ref", "implementation_notes"
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in controls:
            row = {k: c.get(k, "") for k in fields}
            row["frameworks_applicable"] = ", ".join(c["frameworks_applicable"])
            row["soc2_ref"] = c["references"].get("soc2", "")
            row["iso27001_ref"] = c["references"].get("iso27001", "")
            row["hipaa_ref"] = c["references"].get("hipaa", "")
            row["gdpr_ref"] = c["references"].get("gdpr", "")
            writer.writerow(row)
    print(f"✅ Exported {len(controls)} controls to {filepath}")

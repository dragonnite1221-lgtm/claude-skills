# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import FRAMEWORKS  # noqa: E402,E501
# fmt: on


def calculate_framework_coverage(controls: list[dict]) -> dict:
    """Calculate per-framework coverage statistics."""
    coverage = {}
    for fw in FRAMEWORKS:
        applicable = [c for c in controls if fw in c["frameworks_applicable"]]
        implemented = [c for c in applicable if c["status"] in ("Implemented", "Verified")]
        in_progress = [c for c in applicable if c["status"] == "In Progress"]
        not_started = [c for c in applicable if c["status"] == "Not Started"]

        total_effort = sum(c["effort_days"] for c in applicable)
        remaining_effort = sum(
            c["effort_days"] for c in applicable
            if c["status"] not in ("Implemented", "Verified")
        )
        total_cost = sum(c["cost_usd"] for c in applicable)
        remaining_cost = sum(
            c["cost_usd"] for c in applicable
            if c["status"] not in ("Implemented", "Verified")
        )

        pct_complete = (len(implemented) / len(applicable) * 100) if applicable else 0

        coverage[fw] = {
            "framework": FRAMEWORKS[fw]["name"],
            "total_controls": len(applicable),
            "implemented": len(implemented),
            "in_progress": len(in_progress),
            "not_started": len(not_started),
            "pct_complete": pct_complete,
            "total_effort_days": total_effort,
            "remaining_effort_days": remaining_effort,
            "total_cost_usd": total_cost,
            "remaining_cost_usd": remaining_cost,
            "gap_controls": [c["name"] for c in not_started],
        }

    return coverage
def find_high_leverage_controls(controls: list[dict]) -> list[dict]:
    """Controls that satisfy the most frameworks — highest ROI to implement."""
    multi_fw = [c for c in controls if c["framework_count"] >= 3
                and c["status"] not in ("Implemented", "Verified")]
    return sorted(multi_fw, key=lambda c: (-c["framework_count"], c["effort_days"]))
def estimate_roadmap(controls: list[dict], target_frameworks: list[str]) -> list[dict]:
    """
    Generate an ordered implementation roadmap for target frameworks.
    Prioritize: (1) controls blocking most frameworks, (2) quick wins (low effort).
    """
    applicable = [c for c in controls
                  if any(fw in c["frameworks_applicable"] for fw in target_frameworks)
                  and c["status"] not in ("Implemented", "Verified")]

    # Score: (frameworks_covered × 10) - (effort_days) → higher is better
    for c in applicable:
        fw_overlap = len([fw for fw in target_frameworks if fw in c["frameworks_applicable"]])
        c["_priority_score"] = (fw_overlap * 10) - c["effort_days"]

    return sorted(applicable, key=lambda c: -c["_priority_score"])
def fmt_dollars(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:.0f}"
def status_icon(status: str) -> str:
    icons = {
        "Implemented": "✅",
        "Verified": "✅",
        "In Progress": "🔄",
        "Not Started": "⬜",
        "Planned": "📋",
    }
    return icons.get(status, "❓")
def print_header():
    print("\n" + "=" * 80)
    print("  CISO COMPLIANCE TRACKER — Multi-Framework Coverage")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)
def print_framework_summary(coverage: dict):
    print("\n📋 FRAMEWORK COVERAGE SUMMARY")
    print("-" * 80)
    header = f"{'Framework':<20} {'Done':<6} {'WIP':<5} {'Gap':<5} {'Complete':<10} {'Remain Cost':<14} {'Remain Days'}"
    print(header)
    print("-" * 80)
    for fw_id, data in coverage.items():
        pct = f"{data['pct_complete']:.0f}%"
        print(
            f"{data['framework']:<20} {data['implemented']:<6} {data['in_progress']:<5} "
            f"{data['not_started']:<5} {pct:<10} {fmt_dollars(data['remaining_cost_usd']):<14} "
            f"{data['remaining_effort_days']} days"
        )
def print_control_table(controls: list[dict], framework_filter: Optional[str] = None):
    filtered = controls
    if framework_filter:
        filtered = [c for c in controls if framework_filter in c["frameworks_applicable"]]

    title = f"CONTROL DOMAINS"
    if framework_filter:
        title += f" — {FRAMEWORKS[framework_filter]['name']}"

    print(f"\n🔧 {title}")
    print("-" * 90)
    header = f"{'ID':<14} {'Control Name':<30} {'Frameworks':<8} {'Effort':<8} {'Cost':<10} {'Status'}"
    print(header)
    print("-" * 90)

    for c in filtered:
        fw_badges = "/".join(
            fw.upper()[:3] for fw in ["soc2", "iso27001", "hipaa", "gdpr"]
            if fw in c["frameworks_applicable"]
        )
        icon = status_icon(c["status"])
        print(
            f"{c['domain_id']:<14} {c['name'][:29]:<30} {fw_badges:<8} "
            f"{c['effort_days']:>3}d    {fmt_dollars(c['cost_usd']):<10} {icon} {c['status']}"
        )
def print_gap_analysis(coverage: dict):
    print("\n⚠️  GAP ANALYSIS — Controls Not Yet Started")
    print("-" * 70)
    for fw_id, data in coverage.items():
        if data["gap_controls"]:
            print(f"\n  {data['framework']} — {len(data['gap_controls'])} gaps:")
            for gap in data["gap_controls"]:
                print(f"    • {gap}")

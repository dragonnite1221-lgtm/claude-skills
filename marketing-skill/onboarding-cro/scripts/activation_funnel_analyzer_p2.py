# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from activation_funnel_analyzer_base import *  # noqa: F403,E402
# fmt: off
from activation_funnel_analyzer_p1 import analyze_funnel  # noqa: E402,E501
# fmt: on


def format_report(result):
    """Format human-readable report."""
    lines = []
    lines.append("")
    lines.append("=" * 65)
    lines.append("  ONBOARDING FUNNEL — ACTIVATION ANALYSIS")
    lines.append("=" * 65)
    lines.append("")

    summary = result["summary"]
    score = summary["score"]
    bar = "█" * (score // 5) + "░" * (20 - score // 5)

    lines.append(f"  ACTIVATION SCORE: {score}/100")
    lines.append(f"  [{bar}]")
    lines.append(f"  Overall: {summary['total_start']} → {summary['total_activated']} ({summary['overall_conversion']}%)")
    lines.append("")

    # Funnel visualization
    lines.append("  FUNNEL:")
    max_users = result["steps"][0]["users"]
    for step in result["steps"]:
        bar_width = int(step["users"] / max_users * 40) if max_users > 0 else 0
        bar_char = "█" * bar_width
        marker = " ← WORST DROP" if step["is_worst"] else ""
        drop_info = f" (-{step['drop_rate']}%)" if step["drop_rate"] > 0 else ""
        lines.append(f"  {bar_char} {step['users']:>5} | {step['step']}{drop_info}{marker}")

    lines.append("")

    # Step-by-step breakdown
    lines.append("  STEP BREAKDOWN:")
    lines.append(f"  {'Step':<25} {'Users':>7} {'From Start':>12} {'Drop':>8} {'Lost':>7}")
    lines.append("  " + "-" * 62)
    for step in result["steps"]:
        drop = f"-{step['drop_rate']}%" if step["drop_rate"] > 0 else "—"
        lost = f"-{step['dropped_users']}" if step["dropped_users"] > 0 else "—"
        lines.append(f"  {step['step']:<25} {step['users']:>7} {step['rate_from_start']:>10.1f}% {drop:>8} {lost:>7}")
    lines.append("")

    # Improvement potential
    if result["improvements"]:
        lines.append("  💡 IMPROVEMENT POTENTIAL:")
        for imp in result["improvements"]:
            lines.append(f"     Action: {imp['action']}")
            lines.append(f"     Drop: {imp['current_drop']} → {imp['target_drop']}")
            lines.append(f"     Users saved at step: +{imp['users_saved']}")
            lines.append(f"     Additional activated: +{imp['additional_activated']}")
            lines.append(f"     Impact on overall rate: {imp['impact_on_overall']}")
        lines.append("")

    return "\n".join(lines)
SAMPLE_DATA = {
    "steps": [
        {"name": "Signup completed", "users": 1000},
        {"name": "Email verified", "users": 840},
        {"name": "Profile setup", "users": 580},
        {"name": "First project created", "users": 290},
        {"name": "Invited teammate", "users": 145},
        {"name": "Aha moment (Day 3)", "users": 95},
        {"name": "Activated (Day 7)", "users": 72}
    ]
}
def main():
    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]

    if args and os.path.isfile(args[0]):
        with open(args[0]) as f:
            data = json.load(f)
    else:
        if not args:
            print("[Demo mode — analyzing sample SaaS onboarding funnel]")
        data = SAMPLE_DATA

    result = analyze_funnel(data)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))

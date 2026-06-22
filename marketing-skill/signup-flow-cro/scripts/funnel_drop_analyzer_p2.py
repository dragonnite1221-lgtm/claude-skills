# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_drop_analyzer_base import *  # noqa: F403,E402
# fmt: off
from funnel_drop_analyzer_p1 import _funnel_score, _score_label, _top_priority, get_recommendation  # noqa: E402,E501
# fmt: on


def analyze_funnel(steps: list) -> dict:
    """
    Analyse a funnel step list and return full metrics + recommendations.

    Each step: {"step": <str>, "count": <int>}
    """
    if not steps:
        raise ValueError("steps list is empty")
    if len(steps) < 2:
        raise ValueError("Need at least 2 steps to analyse a funnel")

    top_count = steps[0]["count"]
    if top_count <= 0:
        raise ValueError("Top-of-funnel count must be > 0")

    step_metrics = []
    worst_step = None
    worst_drop_rate = -1.0

    for i, s in enumerate(steps):
        name  = s["step"]
        count = s["count"]

        cumulative_rate = count / top_count

        if i == 0:
            step_to_step_rate = 1.0
            drop_count        = 0
            drop_rate         = 0.0
            recommendations   = ["Top of funnel — all visitors enter here."]
        else:
            prev_count        = steps[i - 1]["count"]
            step_to_step_rate = count / prev_count if prev_count > 0 else 0.0
            drop_count        = prev_count - count
            drop_rate         = 1 - step_to_step_rate
            recommendations   = get_recommendation(name, drop_rate)

            if drop_rate > worst_drop_rate:
                worst_drop_rate = drop_rate
                worst_step      = name

        step_metrics.append({
            "step":               name,
            "count":              count,
            "step_conversion_pct":   round(step_to_step_rate * 100, 2),
            "step_drop_pct":         round(drop_rate * 100, 2),
            "drop_count":            drop_count,
            "cumulative_conversion_pct": round(cumulative_rate * 100, 2),
            "recommendations":    recommendations,
        })

    # Overall funnel health score (0-100)
    overall_conv = steps[-1]["count"] / top_count
    score = _funnel_score(step_metrics, overall_conv)

    return {
        "summary": {
            "total_steps":               len(steps),
            "top_of_funnel_count":        top_count,
            "bottom_of_funnel_count":     steps[-1]["count"],
            "overall_conversion_pct":     round(overall_conv * 100, 2),
            "worst_performing_step":      worst_step,
            "worst_step_drop_pct":        round(worst_drop_rate * 100, 2),
            "funnel_health_score":        score,
            "funnel_health_label":        _score_label(score),
        },
        "steps": step_metrics,
        "top_priority": _top_priority(step_metrics),
    }
def pretty_print(result: dict) -> None:
    s   = result["summary"]
    tp  = result["top_priority"]

    print("\n" + "=" * 65)
    print("  SIGNUP FUNNEL DROP-OFF ANALYZER")
    print("=" * 65)

    print(f"\n📊  FUNNEL OVERVIEW")
    print(f"  Top of funnel      : {s['top_of_funnel_count']:,} visitors")
    print(f"  Bottom of funnel   : {s['bottom_of_funnel_count']:,} converted")
    print(f"  Overall conversion : {s['overall_conversion_pct']}%")
    print(f"  Funnel health      : {s['funnel_health_score']}/100  ({s['funnel_health_label']})")
    print(f"  Worst step         : {s['worst_performing_step']}  "
          f"({s['worst_step_drop_pct']}% drop)")

    print(f"\n{'Step':<28} {'Count':>8}  {'Step Conv':>10}  {'Step Drop':>10}  {'Cumul Conv':>10}")
    print("─" * 75)
    for m in result["steps"]:
        bar = "█" * int(m["cumulative_conversion_pct"] / 5)
        print(f"  {m['step']:<26} {m['count']:>8,}  "
              f"{m['step_conversion_pct']:>9.1f}%  "
              f"{m['step_drop_pct']:>9.1f}%  "
              f"{m['cumulative_conversion_pct']:>9.1f}%  {bar}")

    print(f"\n🚨  TOP PRIORITY FIX: {tp.get('step', 'N/A')}")
    print(f"  Lost visitors : {tp.get('drop_count', 0):,}  ({tp.get('drop_pct', 0)}% drop)")
    print(f"  Why fix first : {tp.get('why', '')}")
    print("  Quick wins:")
    for qw in tp.get("quick_wins", []):
        print(f"    • {qw}")

    print(f"\n💡  STEP-BY-STEP RECOMMENDATIONS")
    for m in result["steps"][1:]:
        if m["step_drop_pct"] > 10:
            print(f"\n  [{m['step']}]  ↓{m['step_drop_pct']}% drop")
            for r in m["recommendations"]:
                print(f"    • {r}")

    print()
DEMO_STEPS = [
    {"step": "Landing Page Visit",   "count": 12000},
    {"step": "Clicked Sign Up CTA",  "count": 4560},
    {"step": "Filled Registration",  "count": 2800},
    {"step": "Email Verified",       "count": 1540},
    {"step": "Onboarding Completed", "count":  880},
    {"step": "First Core Action",    "count":  420},
]
def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyse signup funnel drop-off by step (stdlib only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--steps",  type=str, default=None,
                        help="Path to JSON file with funnel steps")
    parser.add_argument("--stdin",  action="store_true",
                        help="Read steps JSON from stdin")
    parser.add_argument("--json",   action="store_true",
                        help="Output results as JSON")
    return parser.parse_args()

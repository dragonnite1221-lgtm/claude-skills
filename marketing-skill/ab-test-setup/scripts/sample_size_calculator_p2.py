# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sample_size_calculator_base import *  # noqa: F403,E402
# fmt: off
from sample_size_calculator_p1 import _score_label  # noqa: E402,E501
# fmt: on


def score_test_design(result: dict) -> dict:
    """Heuristic quality score for the A/B test design."""
    score = 100
    reasons = []
    inputs = result["inputs"]

    # Penalise very low baseline (unreliable estimates)
    if inputs["baseline_conversion_rate"] < 0.01:
        score -= 15
        reasons.append("Baseline <1%: high variance, consider aggregating more data first.")

    # Penalise tiny MDE (will need enormous sample)
    mde = inputs["minimum_detectable_effect_relative"]
    if mde < 0.05:
        score -= 20
        reasons.append("MDE <5%: very small effect, experiment may take months.")
    elif mde < 0.10:
        score -= 10
        reasons.append("MDE <10%: moderately small effect size.")

    # Penalise overly aggressive alpha
    if inputs["significance_level_alpha"] > 0.10:
        score -= 15
        reasons.append("α >10%: high false-positive risk.")

    # Penalise low power
    if inputs["statistical_power"] < 0.80:
        score -= 20
        reasons.append("Power <80%: elevated risk of missing real effects (Type II error).")

    # Duration penalty (if available)
    dur = result.get("duration")
    if dur:
        days = dur["estimated_days"]
        if days > 90:
            score -= 20
            reasons.append(f"Test duration {days}d >90 days: novelty/seasonal effects likely.")
        elif days > 30:
            score -= 10
            reasons.append(f"Test duration {days}d >30 days: monitor for external confounders.")

    score = max(0, score)
    return {
        "design_quality_score": score,
        "score_interpretation": _score_label(score),
        "issues": reasons if reasons else ["No major design issues detected."],
    }
def pretty_print(result: dict, score: dict) -> None:
    inp = result["inputs"]
    res = result["results"]
    zs  = result["z_scores"]

    print("\n" + "=" * 60)
    print("  A/B TEST SAMPLE SIZE CALCULATOR")
    print("=" * 60)

    print("\n📥  INPUTS")
    print(f"  Baseline conversion rate : {inp['baseline_conversion_rate']*100:.2f}%")
    print(f"  Variant conversion rate  : {inp['expected_variant_conversion_rate']*100:.2f}%")
    print(f"  Minimum detectable effect: {inp['minimum_detectable_effect_relative']*100:.1f}% relative "
          f"(+{res['absolute_lift']*100:.3f}pp absolute)")
    print(f"  Significance level (α)   : {inp['significance_level_alpha']}")
    print(f"  Statistical power        : {inp['statistical_power']*100:.0f}%")

    print("\n📐  FORMULA")
    print(f"  {result['formula']}")
    print(f"  Z_α/2 = {zs['z_alpha_2']}   Z_β = {zs['z_beta']}")

    print("\n📊  RESULTS")
    print(f"  ✅ Sample size per variation : {res['sample_size_per_variation']:,}")
    print(f"  ✅ Total sample size (both)  : {res['total_sample_size']:,}")

    if "duration" in result:
        d = result["duration"]
        print(f"\n⏱️   DURATION ESTIMATE  (traffic: {d['daily_traffic_both_variants']:,}/day)")
        print(f"  Estimated test duration : {d['estimated_days']} days  (~{d['estimated_weeks']} weeks)")
        print(f"  Note: {d['note']}")

    print("\n💡  ASSUMPTIONS")
    for a in result["assumptions"]:
        print(f"  • {a}")

    print(f"\n🎯  DESIGN QUALITY SCORE: {score['design_quality_score']}/100  ({score['score_interpretation']})")
    for issue in score["issues"]:
        print(f"  ⚠  {issue}")

    print()
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate required sample size for an A/B test (stdlib only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--baseline",       type=float, default=None,
                        help="Baseline conversion rate (e.g. 0.05 for 5%%)")
    parser.add_argument("--mde",            type=float, default=None,
                        help="Minimum detectable effect as relative lift (e.g. 0.20 for +20%%)")
    parser.add_argument("--alpha",          type=float, default=0.05,
                        help="Significance level α (default: 0.05)")
    parser.add_argument("--power",          type=float, default=0.80,
                        help="Statistical power 1-β (default: 0.80)")
    parser.add_argument("--daily-traffic",  type=int,   default=None,
                        help="Total daily visitors across both variants (for duration estimate)")
    parser.add_argument("--json",           action="store_true",
                        help="Output results as JSON")
    return parser.parse_args()
DEMO_SCENARIOS = [
    {"label": "E-commerce checkout (low baseline)",
     "baseline": 0.03, "mde": 0.20, "alpha": 0.05, "power": 0.80, "daily_traffic": 800},
    {"label": "SaaS free-trial signup (medium baseline)",
     "baseline": 0.08, "mde": 0.15, "alpha": 0.05, "power": 0.80, "daily_traffic": 2000},
    {"label": "Button CTA (high baseline)",
     "baseline": 0.25, "mde": 0.10, "alpha": 0.05, "power": 0.80, "daily_traffic": 5000},
]

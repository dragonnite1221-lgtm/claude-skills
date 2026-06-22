# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_drop_analyzer_base import *  # noqa: F403,E402


RECOMMENDATIONS = {
    "high_drop": {
        "threshold": 0.50,   # >50% drop
        "landing_page": [
            "Value proposition may be unclear — run a 5-second test.",
            "Add social proof (testimonials, logos, user count) above the fold.",
            "Ensure CTA button is prominent and benefit-focused ('Start Free' not 'Submit').",
        ],
        "clicked_sign_up": [
            "CTA label or placement may not resonate — A/B test button copy and colour.",
            "Users may not trust the product — add trust badges and reviews near CTA.",
            "Consider a sticky header CTA for long landing pages.",
        ],
        "filled_form": [
            "Form has too many fields — reduce to email + password minimum.",
            "Try progressive disclosure: collect extra info post-signup.",
            "Add inline validation so errors appear in real-time, not on submit.",
            "Show a progress indicator if multi-step.",
        ],
        "email_verified": [
            "Verification email may land in spam — check SPF/DKIM/DMARC.",
            "Send a plain-text follow-up 30 min after signup nudging verification.",
            "Consider SMS or magic-link alternatives to email verification.",
            "Reduce time-to-value: show a useful screen before requiring verification.",
        ],
        "default": [
            "Significant drop detected — instrument with session recordings (Hotjar/FullStory).",
            "Run exit surveys at this step to capture qualitative reasons.",
            "Check for UI bugs or broken flows on mobile.",
        ],
    },
    "medium_drop": {
        "threshold": 0.25,   # 25–50% drop
        "default": [
            "Moderate friction — review copy and UX at this step.",
            "Ensure mobile experience is frictionless (test on real devices).",
            "Add micro-copy explaining why information is requested.",
        ],
    },
    "healthy": {
        "default": [
            "Step conversion is healthy — focus optimisation effort elsewhere.",
        ],
    },
}
def classify_step_name(name: str) -> str:
    """Map step name to a known category for targeted recommendations."""
    n = name.lower()
    if any(k in n for k in ["land", "visit", "page", "home"]):
        return "landing_page"
    if any(k in n for k in ["cta", "click", "signup", "sign up", "register", "start"]):
        return "clicked_sign_up"
    if any(k in n for k in ["form", "fill", "detail", "info", "enter"]):
        return "filled_form"
    if any(k in n for k in ["email", "verif", "confirm", "activate"]):
        return "email_verified"
    return "default"
def get_recommendation(step_name: str, drop_rate: float) -> list:
    if drop_rate > RECOMMENDATIONS["high_drop"]["threshold"]:
        bucket = RECOMMENDATIONS["high_drop"]
        cat = classify_step_name(step_name)
        return bucket.get(cat, bucket["default"])
    elif drop_rate > RECOMMENDATIONS["medium_drop"]["threshold"]:
        return RECOMMENDATIONS["medium_drop"]["default"]
    else:
        return RECOMMENDATIONS["healthy"]["default"]
def _funnel_score(step_metrics: list, overall_conv: float) -> int:
    """
    Score = 100 * overall_conversion adjusted for worst-step severity.
    - Base: log-scale overall conversion (capped at a 10% target = 100 pts)
    - Penalty: each step with >60% drop deducts points
    """
    target_conv = 0.10  # 10% overall = score 100
    base = min(100, math.log1p(overall_conv) / math.log1p(target_conv) * 100)

    penalty = 0
    for m in step_metrics[1:]:
        if m["step_drop_pct"] > 60:
            penalty += 10
        elif m["step_drop_pct"] > 40:
            penalty += 5

    score = max(0, round(base - penalty))
    return score
def _score_label(s: int) -> str:
    if s >= 80: return "Excellent"
    if s >= 60: return "Good"
    if s >= 40: return "Fair"
    if s >= 20: return "Poor"
    return "Critical"
def _top_priority(step_metrics: list) -> dict:
    """Return the single highest-impact step to fix first."""
    # Pick step with largest absolute drop count (not just rate)
    candidates = step_metrics[1:]
    if not candidates:
        return {}
    top = max(candidates, key=lambda m: m["drop_count"])
    return {
        "step":             top["step"],
        "drop_count":       top["drop_count"],
        "drop_pct":         top["step_drop_pct"],
        "why":              "Largest absolute visitor loss — highest revenue impact.",
        "quick_wins":       top["recommendations"],
    }

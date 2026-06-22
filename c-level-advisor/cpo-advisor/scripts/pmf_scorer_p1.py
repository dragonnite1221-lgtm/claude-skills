# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pmf_scorer_base import *  # noqa: F403,E402


def sample_data() -> dict:
    """
    Sample input data. Replace with your own values.

    All fields are optional — missing fields score 0 for that sub-metric
    and a note is added to recommendations.
    """
    return {
        "product_name": "Acme SaaS",
        "business_model": "b2b_saas",  # b2b_saas | consumer | marketplace | plg

        # Retention: D30 and D90 as decimals (e.g. 0.42 = 42%)
        # Provide multiple cohorts if available. Most recent first.
        "retention": {
            "d30_cohorts": [0.38, 0.41, 0.44, 0.43],  # newest → oldest
            "d90_cohorts": [0.28, 0.30, 0.31],
            "curve_flattening": True,  # Does the curve flatten (vs. continuing to drop)?
        },

        # Engagement
        "engagement": {
            "dau_mau_ratio": 0.24,           # Daily active / Monthly active (decimal)
            "avg_sessions_per_week": 3.2,    # Per active user
            "key_action_rate": 0.55,         # % of users who performed core value action in last 30d
            "session_depth_score": 0.6,      # 0-1: 0 = one page, 1 = full feature exploration
        },

        # Satisfaction
        "satisfaction": {
            "sean_ellis_very_disappointed": 0.38,  # Fraction (e.g. 0.38 = 38%)
            "sean_ellis_sample_size": 87,           # Raw response count
            "nps_score": 34,                        # -100 to 100
            "nps_sample_size": 210,
        },

        # Growth
        "growth": {
            "organic_signup_pct": 0.27,     # % of new signups from organic/referral/WOM
            "referral_rate": 0.18,          # % of active users who referred someone last 90d
            "mom_growth_rate": 0.08,        # Month-over-month new user growth (decimal)
        },
    }
THRESHOLDS = {
    "b2b_saas": {
        "d30_pmf": 0.40,   "d30_strong": 0.60,
        "d90_pmf": 0.25,   "d90_strong": 0.45,
        "dau_mau_pmf": 0.15, "dau_mau_strong": 0.35,
        "sean_ellis_pmf": 0.40, "sean_ellis_strong": 0.55,
        "nps_pmf": 30, "nps_strong": 50,
    },
    "consumer": {
        "d30_pmf": 0.20,   "d30_strong": 0.35,
        "d90_pmf": 0.10,   "d90_strong": 0.20,
        "dau_mau_pmf": 0.20, "dau_mau_strong": 0.40,
        "sean_ellis_pmf": 0.40, "sean_ellis_strong": 0.55,
        "nps_pmf": 20, "nps_strong": 45,
    },
    "marketplace": {
        "d30_pmf": 0.30,   "d30_strong": 0.50,
        "d90_pmf": 0.20,   "d90_strong": 0.35,
        "dau_mau_pmf": 0.15, "dau_mau_strong": 0.30,
        "sean_ellis_pmf": 0.40, "sean_ellis_strong": 0.55,
        "nps_pmf": 25, "nps_strong": 45,
    },
    "plg": {
        "d30_pmf": 0.25,   "d30_strong": 0.45,
        "d90_pmf": 0.15,   "d90_strong": 0.30,
        "dau_mau_pmf": 0.20, "dau_mau_strong": 0.40,
        "sean_ellis_pmf": 0.40, "sean_ellis_strong": 0.55,
        "nps_pmf": 30, "nps_strong": 50,
    },
}
DIMENSION_WEIGHTS = {
    "retention":    0.40,
    "engagement":   0.25,
    "satisfaction": 0.20,
    "growth":       0.15,
}
def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
def score_between(value: Optional[float], lo: float, hi: float) -> float:
    """Linear interpolation: lo → 0.0, hi → 1.0, beyond hi → 1.0."""
    if value is None:
        return 0.0
    if value <= lo:
        return 0.0
    if value >= hi:
        return 1.0
    return (value - lo) / (hi - lo)
def cohort_trend(cohorts: list) -> float:
    """
    Given cohorts newest-first, return a trend score -1 to +1.
    Positive = improving. Negative = degrading.
    """
    if len(cohorts) < 2:
        return 0.0
    # Simple: compare most recent half average vs. older half average
    mid = len(cohorts) // 2
    recent_avg = sum(cohorts[:mid]) / mid if mid else cohorts[0]
    older_avg = sum(cohorts[mid:]) / (len(cohorts) - mid)
    if older_avg == 0:
        return 0.0
    delta = (recent_avg - older_avg) / older_avg
    return clamp(delta * 5, -1.0, 1.0)  # scale: 20% improvement = score of 1.0

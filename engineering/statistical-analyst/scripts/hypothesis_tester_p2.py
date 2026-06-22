# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hypothesis_tester_base import *  # noqa: F403,E402
# fmt: off
from hypothesis_tester_p1 import cohens_d, cohens_h, effect_label, normal_ppf, two_tail_p_normal, two_tail_p_t  # noqa: E402,E501
# fmt: on


def ztest_proportions(cn: int, cx: int, tn: int, tx: int, alpha: float) -> dict:
    """Two-proportion Z-test."""
    if cn <= 0 or tn <= 0:
        return {"error": "Sample sizes must be positive."}

    p_c = cx / cn
    p_t = tx / tn
    p_pool = (cx + tx) / (cn + tn)

    se = math.sqrt(p_pool * (1 - p_pool) * (1 / cn + 1 / tn))
    if se == 0:
        return {"error": "Standard error is zero — check input values."}

    z = (p_t - p_c) / se
    p_value = two_tail_p_normal(z)

    # Confidence interval for difference (unpooled SE)
    se_diff = math.sqrt(p_c * (1 - p_c) / cn + p_t * (1 - p_t) / tn)
    z_crit = normal_ppf(1 - alpha / 2)
    diff = p_t - p_c
    ci_lo = diff - z_crit * se_diff
    ci_hi = diff + z_crit * se_diff

    h = cohens_h(p_t, p_c)
    lift = (p_t - p_c) / p_c * 100 if p_c else 0

    return {
        "test": "Two-proportion Z-test",
        "control": {"n": cn, "conversions": cx, "rate": round(p_c, 6)},
        "treatment": {"n": tn, "conversions": tx, "rate": round(p_t, 6)},
        "difference": round(diff, 6),
        "relative_lift_pct": round(lift, 2),
        "z_statistic": round(z, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "confidence_interval": {
            "level": f"{int((1 - alpha) * 100)}%",
            "lower": round(ci_lo, 6),
            "upper": round(ci_hi, 6),
        },
        "effect_size": {
            "cohens_h": round(abs(h), 4),
            "interpretation": effect_label(h, "h"),
        },
    }
def ttest_means(cm: float, cs: float, cn: int, tm: float, ts: float, tn: int, alpha: float) -> dict:
    """Welch's two-sample t-test (unequal variances)."""
    if cn < 2 or tn < 2:
        return {"error": "Each group needs at least 2 observations."}

    se = math.sqrt(cs ** 2 / cn + ts ** 2 / tn)
    if se == 0:
        return {"error": "Standard error is zero — check std values."}

    t = (tm - cm) / se

    # Welch–Satterthwaite degrees of freedom
    num = (cs ** 2 / cn + ts ** 2 / tn) ** 2
    denom = (cs ** 2 / cn) ** 2 / (cn - 1) + (ts ** 2 / tn) ** 2 / (tn - 1)
    df = num / denom if denom else cn + tn - 2

    p_value = two_tail_p_t(t, df)

    z_crit = normal_ppf(1 - alpha / 2) if df > 1000 else normal_ppf(1 - alpha / 2)
    # Use t critical value approximation
    from_t = abs(t) / (p_value / 2) if p_value > 0 else z_crit  # rough
    t_crit = normal_ppf(1 - alpha / 2)  # normal approx for CI

    diff = tm - cm
    ci_lo = diff - t_crit * se
    ci_hi = diff + t_crit * se

    d = cohens_d(tm, ts, tn, cm, cs, cn)
    lift = (tm - cm) / cm * 100 if cm else 0

    return {
        "test": "Welch's two-sample t-test",
        "control": {"n": cn, "mean": round(cm, 4), "std": round(cs, 4)},
        "treatment": {"n": tn, "mean": round(tm, 4), "std": round(ts, 4)},
        "difference": round(diff, 4),
        "relative_lift_pct": round(lift, 2),
        "t_statistic": round(t, 4),
        "degrees_of_freedom": round(df, 1),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "confidence_interval": {
            "level": f"{int((1 - alpha) * 100)}%",
            "lower": round(ci_lo, 4),
            "upper": round(ci_hi, 4),
        },
        "effect_size": {
            "cohens_d": round(abs(d), 4),
            "interpretation": effect_label(d, "d"),
        },
    }

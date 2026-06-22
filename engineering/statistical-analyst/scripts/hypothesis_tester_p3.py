# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hypothesis_tester_base import *  # noqa: F403,E402
# fmt: off
from hypothesis_tester_p1 import cramers_v, effect_label  # noqa: E402,E501
# fmt: on


def _regularized_gamma(a: float, x: float) -> float:
    """Lower regularized incomplete gamma P(a, x) via series expansion."""
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0
    if x < a + 1:
        # Series expansion
        ap = a
        delta = 1.0 / a
        total = delta
        for _ in range(300):
            ap += 1
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-10:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    else:
        # Continued fraction (Lentz)
        b = x + 1 - a
        c = 1e30
        d = 1 / b
        f = d
        for i in range(1, 300):
            an = -i * (i - a)
            b += 2
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1 / d
            delta = d * c
            f *= delta
            if abs(delta - 1) < 1e-10:
                break
        return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * f
def _chi2_cdf(x: float, k: float) -> float:
    """CDF of chi-square via regularized lower incomplete gamma."""
    if x <= 0:
        return 0.0
    return _regularized_gamma(k / 2, x / 2)
def chi2_test(observed: list[float], expected: list[float], alpha: float) -> dict:
    """Chi-square goodness-of-fit test."""
    if len(observed) != len(expected):
        return {"error": "Observed and expected must have the same number of categories."}
    if any(e <= 0 for e in expected):
        return {"error": "Expected values must all be positive."}
    if any(e < 5 for e in expected):
        return {"warning": "Some expected values < 5 — chi-square approximation may be unreliable.",
                "suggestion": "Consider combining categories or using Fisher's exact test."}

    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
    k = len(observed)
    df = k - 1
    n = sum(observed)

    # Chi-square CDF via regularized gamma function approximation
    p_value = 1 - _chi2_cdf(chi2, df)

    v = cramers_v(chi2, int(n), k)

    return {
        "test": "Chi-square goodness-of-fit",
        "categories": k,
        "observed": observed,
        "expected": expected,
        "chi2_statistic": round(chi2, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "effect_size": {
            "cramers_v": round(v, 4),
            "interpretation": effect_label(v, "v"),
        },
    }
DIRECTION = {True: "statistically significant", False: "NOT statistically significant"}

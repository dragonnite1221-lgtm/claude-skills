# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hypothesis_tester_base import *  # noqa: F403,E402


def normal_cdf(z: float) -> float:
    """Cumulative distribution function of standard normal using math.erfc."""
    return 0.5 * math.erfc(-z / math.sqrt(2))
def normal_ppf(p: float) -> float:
    """Percent-point function (inverse CDF) of standard normal via bisection."""
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
def _regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """Regularized incomplete beta I_x(a,b) via continued fraction expansion."""
    if x < 0 or x > 1:
        return 0.0
    if x == 0:
        return 0.0
    if x == 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta) / a
    # Use symmetry for better convergence
    if x > (a + 1) / (a + b + 2):
        return 1 - _regularized_incomplete_beta(1 - x, b, a)
    # Lentz continued fraction
    TINY = 1e-30
    f = TINY
    C = f
    D = 0.0
    for m in range(200):
        for s in (0, 1):
            if m == 0 and s == 0:
                num = 1.0
            elif s == 0:
                num = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
            else:
                num = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))
            D = 1 + num * D
            if abs(D) < TINY:
                D = TINY
            D = 1 / D
            C = 1 + num / C
            if abs(C) < TINY:
                C = TINY
            f *= C * D
            if abs(C * D - 1) < 1e-10:
                break
    return front * f
def t_cdf(t: float, df: float) -> float:
    """
    CDF of t-distribution via regularized incomplete beta function approximation.
    Uses the relation: P(T ≤ t) = I_{x}(df/2, 1/2) where x = df/(df+t^2).
    Falls back to normal CDF for large df (> 1000).
    """
    if df > 1000:
        return normal_cdf(t)
    x = df / (df + t * t)
    # Regularized incomplete beta via continued fraction (Lentz)
    ib = _regularized_incomplete_beta(x, df / 2, 0.5)
    p = ib / 2
    return p if t <= 0 else 1 - p
def two_tail_p_normal(z: float) -> float:
    return 2 * (1 - normal_cdf(abs(z)))
def two_tail_p_t(t: float, df: float) -> float:
    return 2 * (1 - t_cdf(abs(t), df))
def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h for two proportions."""
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))
def cohens_d(mean1: float, std1: float, n1: int, mean2: float, std2: float, n2: int) -> float:
    """Cohen's d using pooled standard deviation."""
    pooled = math.sqrt(((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / (n1 + n2 - 2))
    return (mean1 - mean2) / pooled if pooled else 0.0
def cramers_v(chi2: float, n: int, k: int) -> float:
    """Cramér's V effect size for chi-square test."""
    return math.sqrt(chi2 / (n * (k - 1))) if n and k > 1 else 0.0
def effect_label(val: float, metric: str) -> str:
    thresholds = {"h": [0.2, 0.5, 0.8], "d": [0.2, 0.5, 0.8], "v": [0.1, 0.3, 0.5]}
    t = thresholds.get(metric, [0.2, 0.5, 0.8])
    v = abs(val)
    if v < t[0]:
        return "negligible"
    if v < t[1]:
        return "small"
    if v < t[2]:
        return "medium"
    return "large"

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sample_size_calculator_base import *  # noqa: F403,E402


def _norm_ppf(p: float) -> float:
    """Percent-point function (inverse CDF) of the standard normal.
    Uses rational approximation — accurate to ~1e-9.
    Reference: Abramowitz & Stegun 26.2.17 / Peter Acklam's algorithm.
    """
    if p <= 0 or p >= 1:
        raise ValueError(f"p must be in (0, 1), got {p}")

    # Coefficients for rational approximation
    a = [-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00]
    d = [7.784695709041462e-03,  3.224671290700398e-01,
         2.445134137142996e+00,  3.754408661907416e+00]

    p_low  = 0.02425
    p_high = 1 - p_low

    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
def calculate_sample_size(
    baseline: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict:
    """
    Two-proportion z-test sample size formula (two-tailed).

    n = (Z_alpha/2 + Z_beta)^2 * (p1*(1-p1) + p2*(1-p2)) / (p2 - p1)^2

    Args:
        baseline  : baseline conversion rate (e.g. 0.05 for 5%)
        mde       : minimum detectable effect as relative lift (e.g. 0.20 for +20%)
        alpha     : significance level (Type I error rate), default 0.05
        power     : statistical power (1 - Type II error rate), default 0.80

    Returns dict with all intermediate values and results.
    """
    p1 = baseline
    p2 = baseline * (1 + mde)          # expected conversion with treatment

    if not (0 < p1 < 1):
        raise ValueError(f"baseline must be in (0,1), got {p1}")
    if not (0 < p2 < 1):
        raise ValueError(
            f"baseline * (1 + mde) = {p2:.4f} is outside (0,1). "
            "Reduce mde or increase baseline."
        )

    z_alpha = _norm_ppf(1 - alpha / 2)   # two-tailed
    z_beta  = _norm_ppf(power)

    pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
    effect_sq  = (p2 - p1) ** 2

    n_raw = ((z_alpha + z_beta) ** 2 * pooled_var) / effect_sq
    n     = math.ceil(n_raw)

    return {
        "inputs": {
            "baseline_conversion_rate": p1,
            "minimum_detectable_effect_relative": mde,
            "expected_variant_conversion_rate": round(p2, 6),
            "significance_level_alpha": alpha,
            "statistical_power": power,
        },
        "z_scores": {
            "z_alpha_2": round(z_alpha, 4),
            "z_beta":    round(z_beta,  4),
        },
        "results": {
            "sample_size_per_variation": n,
            "total_sample_size":         n * 2,
            "absolute_lift":             round(p2 - p1, 6),
            "relative_lift_pct":         round(mde * 100, 2),
        },
        "formula": (
            "n = (Z_α/2 + Z_β)² × (p1(1−p1) + p2(1−p2)) / (p2−p1)²  "
            "[two-proportion z-test, two-tailed]"
        ),
        "assumptions": [
            "Two-tailed test (detecting lift in either direction)",
            "Independent samples (no within-subject correlation)",
            "Fixed horizon (not sequential / always-valid)",
            "Binomial outcome (conversion yes/no)",
            "No novelty effect correction applied",
        ],
    }
def add_duration(result: dict, daily_traffic: int) -> dict:
    """Append estimated test duration given total daily traffic (both variants)."""
    n_total = result["results"]["total_sample_size"]
    days    = math.ceil(n_total / daily_traffic)
    weeks   = round(days / 7, 1)
    result["duration"] = {
        "daily_traffic_both_variants": daily_traffic,
        "estimated_days":  days,
        "estimated_weeks": weeks,
        "note": (
            "Assumes traffic is evenly split 50/50 between control and variant. "
            "Add ~10–20% buffer for weekday/weekend variance."
        ),
    }
    return result
def _score_label(s: int) -> str:
    if s >= 90: return "Excellent"
    if s >= 75: return "Good"
    if s >= 60: return "Fair"
    if s >= 40: return "Poor"
    return "Critical"

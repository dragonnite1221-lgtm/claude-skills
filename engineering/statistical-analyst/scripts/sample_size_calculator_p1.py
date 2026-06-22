# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sample_size_calculator_base import *  # noqa: F403,E402


def normal_cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2))
def normal_ppf(p: float) -> float:
    """Inverse normal CDF via bisection."""
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
def sample_size_proportion(baseline: float, mde: float, alpha: float, power: float) -> int:
    """
    Required n per variant for a two-proportion Z-test.

    Uses the standard formula:
        n = (z_α/2 + z_β)² × (p1(1−p1) + p2(1−p2)) / (p1 − p2)²

    Args:
        baseline: Control conversion rate (e.g. 0.05 for 5%)
        mde: Minimum detectable effect as relative change (e.g. 0.20 for +20% relative)
        alpha: Significance level (e.g. 0.05)
        power: Statistical power (e.g. 0.80)
    """
    p1 = baseline
    p2 = baseline * (1 + mde)

    if not (0 < p1 < 1) or not (0 < p2 < 1):
        raise ValueError(f"Rates must be between 0 and 1. Got baseline={p1}, treatment={p2:.4f}")

    z_alpha = normal_ppf(1 - alpha / 2)
    z_beta = normal_ppf(power)

    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p2 - p1) ** 2

    return math.ceil(numerator / denominator)
def sample_size_mean(baseline_mean: float, baseline_std: float, mde: float, alpha: float, power: float) -> int:
    """
    Required n per variant for a two-sample t-test.

    Uses:
        n = 2 × σ² × (z_α/2 + z_β)² / δ²

    where δ = mde × baseline_mean (absolute effect).

    Args:
        baseline_mean: Control group mean
        baseline_std: Control group standard deviation
        mde: Minimum detectable effect as relative change (e.g. 0.10 for +10%)
        alpha: Significance level
        power: Statistical power
    """
    delta = abs(mde * baseline_mean)
    if delta == 0:
        raise ValueError("MDE × baseline_mean = 0. Cannot size experiment with zero effect.")

    z_alpha = normal_ppf(1 - alpha / 2)
    z_beta = normal_ppf(power)

    n = 2 * baseline_std ** 2 * (z_alpha + z_beta) ** 2 / delta ** 2
    return math.ceil(n)
def duration_estimate(n_per_variant: int, daily_traffic: int | None, variants: int = 2) -> str:
    if daily_traffic and daily_traffic > 0:
        traffic_per_variant = daily_traffic / variants
        days = math.ceil(n_per_variant / traffic_per_variant)
        weeks = days / 7
        return f"{days} days ({weeks:.1f} weeks) at {daily_traffic:,} daily users split {variants} ways"
    return "Provide --daily-traffic to estimate duration"
def print_report(
    test: str, n: int, baseline: float, mde: float, alpha: float, power: float,
    daily_traffic: int | None, variants: int,
    baseline_mean: float | None = None, baseline_std: float | None = None
):
    total = n * variants
    treatment_rate = baseline * (1 + mde) if test == "proportion" else None
    absolute_mde = baseline * mde if test == "proportion" else (baseline_mean or 0) * mde

    print("=" * 60)
    print("  SAMPLE SIZE REPORT")
    print("=" * 60)

    if test == "proportion":
        print(f"  Baseline conversion rate: {baseline:.2%}")
        print(f"  Target conversion rate:   {treatment_rate:.2%}")
        print(f"  MDE: {mde:+.1%} relative  ({absolute_mde:+.4f} absolute)")
    else:
        print(f"  Baseline mean: {baseline_mean}  (std: {baseline_std})")
        print(f"  MDE: {mde:+.1%} relative  (absolute: {absolute_mde:+.4f})")

    print(f"  Significance level (α): {alpha}")
    print(f"  Statistical power (1−β): {power:.0%}")
    print(f"  Variants: {variants}")
    print()
    print(f"  Required per variant:  {n:>10,}")
    print(f"  Required total:        {total:>10,}")
    print()
    print(f"  Duration: {duration_estimate(n, daily_traffic, variants)}")
    print()

    # Risk interpretation
    if n < 100:
        print("  ⚠️  Very small sample — results may be sensitive to outliers.")
    elif n > 1_000_000:
        print("  ⚠️  Very large sample required — consider increasing MDE or accepting lower power.")
    else:
        print("  ✅ Sample size is achievable for most web/app products.")

    print("=" * 60)

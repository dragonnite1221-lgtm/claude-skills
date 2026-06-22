# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sample_size_calculator_base import *  # noqa: F403,E402
# fmt: off
from sample_size_calculator_p1 import print_report, sample_size_mean, sample_size_proportion  # noqa: E402,E501
# fmt: on


def print_table(test: str, baseline: float, mde: float, alpha: float,
                baseline_mean: float | None, baseline_std: float | None):
    """Print tradeoff table across power levels and MDE values."""
    powers = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    mdes = [mde * 0.5, mde * 0.75, mde, mde * 1.5, mde * 2.0]

    print("=" * 70)
    print(f"  SAMPLE SIZE TRADEOFF TABLE  (α={alpha}, baseline={'proportion' if test == 'proportion' else 'mean'})")
    print("=" * 70)
    header = f"  {'MDE':>8} | " + " | ".join(f"power={p:.0%}" for p in powers)
    print(header)
    print("  " + "-" * (len(header) - 2))

    for m in mdes:
        row = f"  {m:>+7.1%} | "
        cells = []
        for p in powers:
            try:
                if test == "proportion":
                    n = sample_size_proportion(baseline, m, alpha, p)
                else:
                    n = sample_size_mean(baseline_mean, baseline_std, m, alpha, p)
                cells.append(f"{n:>9,}")
            except ValueError:
                cells.append(f"{'N/A':>9}")
        row += " | ".join(cells)
        print(row)

    print("=" * 70)
    print("  (Values = required n per variant)")
    print()
def main():
    parser = argparse.ArgumentParser(description="Calculate required sample size for A/B experiments.")
    parser.add_argument("--test", choices=["proportion", "mean"], required=True,
                        help="Type of metric: proportion (conversion rate) or mean (continuous)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
    parser.add_argument("--power", type=float, default=0.80, help="Statistical power (default: 0.80)")
    parser.add_argument("--mde", type=float, required=True,
                        help="Minimum detectable effect as relative change (e.g. 0.20 = +20%%)")
    parser.add_argument("--variants", type=int, default=2, help="Number of variants including control (default: 2)")
    parser.add_argument("--daily-traffic", type=int, help="Daily unique users (for duration estimate)")
    parser.add_argument("--table", action="store_true", help="Print tradeoff table across power and MDE")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    # Proportion-specific
    parser.add_argument("--baseline", type=float, help="Baseline conversion rate (e.g. 0.05 for 5%%)")

    # Mean-specific
    parser.add_argument("--baseline-mean", type=float, help="Control group mean")
    parser.add_argument("--baseline-std", type=float, help="Control group standard deviation")

    args = parser.parse_args()

    try:
        if args.test == "proportion":
            if args.baseline is None:
                print("Error: --baseline is required for proportion test", file=sys.stderr)
                sys.exit(1)
            n = sample_size_proportion(args.baseline, args.mde, args.alpha, args.power)
        else:
            if args.baseline_mean is None or args.baseline_std is None:
                print("Error: --baseline-mean and --baseline-std are required for mean test", file=sys.stderr)
                sys.exit(1)
            n = sample_size_mean(args.baseline_mean, args.baseline_std, args.mde, args.alpha, args.power)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = {
            "test": args.test,
            "n_per_variant": n,
            "n_total": n * args.variants,
            "alpha": args.alpha,
            "power": args.power,
            "mde": args.mde,
            "variants": args.variants,
        }
        if args.test == "proportion":
            output["baseline_rate"] = args.baseline
            output["treatment_rate"] = round(args.baseline * (1 + args.mde), 6)
        else:
            output["baseline_mean"] = args.baseline_mean
            output["baseline_std"] = args.baseline_std
        if args.daily_traffic:
            days = math.ceil(n / (args.daily_traffic / args.variants))
            output["estimated_days"] = days
        print(json.dumps(output, indent=2))
        return

    if args.table:
        print_table(args.test, args.baseline if args.test == "proportion" else None,
                    args.mde, args.alpha, args.baseline_mean, args.baseline_std)

    print_report(
        args.test, n,
        baseline=args.baseline or 0,
        mde=args.mde,
        alpha=args.alpha,
        power=args.power,
        daily_traffic=args.daily_traffic,
        variants=args.variants,
        baseline_mean=args.baseline_mean,
        baseline_std=args.baseline_std,
    )

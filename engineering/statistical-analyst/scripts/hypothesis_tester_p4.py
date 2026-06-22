# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hypothesis_tester_base import *  # noqa: F403,E402
# fmt: off
from hypothesis_tester_p2 import ttest_means, ztest_proportions  # noqa: E402,E501
from hypothesis_tester_p3 import DIRECTION, chi2_test  # noqa: E402,E501
# fmt: on


def verdict(result: dict) -> str:
    if "error" in result:
        return f"ERROR: {result['error']}"
    sig = result.get("significant", False)
    p = result.get("p_value", 1.0)
    alpha = result.get("alpha", 0.05)
    diff = result.get("difference", 0)
    lift = result.get("relative_lift_pct")
    ci = result.get("confidence_interval", {})
    es = result.get("effect_size", {})
    es_name = "Cohen's h" if "cohens_h" in es else ("Cohen's d" if "cohens_d" in es else "Cramér's V")
    es_val = es.get("cohens_h") or es.get("cohens_d") or es.get("cramers_v", 0)
    es_interp = es.get("interpretation", "")

    lines = [
        "",
        "=" * 60,
        f"  {result.get('test', 'Hypothesis Test')}",
        "=" * 60,
    ]

    if "control" in result and "rate" in result["control"]:
        c = result["control"]
        t = result["treatment"]
        lines += [
            f"  Control:   {c['rate']:.4%}  (n={c['n']}, conversions={c['conversions']})",
            f"  Treatment: {t['rate']:.4%}  (n={t['n']}, conversions={t['conversions']})",
            f"  Difference: {diff:+.4%}  ({'+' if lift >= 0 else ''}{lift:.1f}% relative lift)",
        ]
    elif "control" in result and "mean" in result["control"]:
        c = result["control"]
        t = result["treatment"]
        lines += [
            f"  Control:   mean={c['mean']}  std={c['std']}  n={c['n']}",
            f"  Treatment: mean={t['mean']}  std={t['std']}  n={t['n']}",
            f"  Difference: {diff:+.4f}  ({'+' if lift >= 0 else ''}{lift:.1f}% relative lift)",
        ]
    elif "observed" in result:
        lines += [
            f"  Observed: {result['observed']}",
            f"  Expected: {result['expected']}",
        ]

    lines += [
        "",
        f"  p-value:    {p:.6f}  (α={alpha})",
        f"  Result:     {DIRECTION[sig].upper()}",
    ]
    if ci:
        lines.append(f"  {ci['level']} CI: [{ci['lower']}, {ci['upper']}]")
    lines += [
        f"  Effect:     {es_name} = {es_val}  ({es_interp})",
        "",
    ]

    # Plain English verdict
    if sig:
        lines.append(f"  ✅ VERDICT: The difference is real (p={p:.4f} < α={alpha}).")
        if es_interp in ("negligible", "small"):
            lines.append("  ⚠️  BUT: Effect is small — confirm practical significance before shipping.")
        else:
            lines.append("  Effect size is meaningful. Recommend shipping if no negative guardrails.")
    else:
        lines.append(f"  ❌ VERDICT: Insufficient evidence to conclude a difference exists (p={p:.4f} ≥ α={alpha}).")
        lines.append("  Options: extend the test, increase MDE, or kill if underpowered.")

    lines.append("=" * 60)
    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(description="Run hypothesis tests on experiment results.")
    parser.add_argument("--test", choices=["ztest", "ttest", "chi2"], required=True)
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    # Z-test / t-test shared
    parser.add_argument("--control-n", type=int)
    parser.add_argument("--treatment-n", type=int)

    # Z-test
    parser.add_argument("--control-x", type=int, help="Conversions in control group")
    parser.add_argument("--treatment-x", type=int, help="Conversions in treatment group")

    # t-test
    parser.add_argument("--control-mean", type=float)
    parser.add_argument("--control-std", type=float)
    parser.add_argument("--treatment-mean", type=float)
    parser.add_argument("--treatment-std", type=float)

    # chi2
    parser.add_argument("--observed", help="Comma-separated observed counts")
    parser.add_argument("--expected", help="Comma-separated expected counts")

    args = parser.parse_args()

    if args.test == "ztest":
        for req in ["control_n", "control_x", "treatment_n", "treatment_x"]:
            if getattr(args, req) is None:
                print(f"Error: --{req.replace('_', '-')} is required for ztest", file=sys.stderr)
                sys.exit(1)
        result = ztest_proportions(args.control_n, args.control_x, args.treatment_n, args.treatment_x, args.alpha)

    elif args.test == "ttest":
        for req in ["control_n", "control_mean", "control_std", "treatment_n", "treatment_mean", "treatment_std"]:
            if getattr(args, req) is None:
                print(f"Error: --{req.replace('_', '-')} is required for ttest", file=sys.stderr)
                sys.exit(1)
        result = ttest_means(
            args.control_mean, args.control_std, args.control_n,
            args.treatment_mean, args.treatment_std, args.treatment_n,
            args.alpha
        )

    elif args.test == "chi2":
        if not args.observed or not args.expected:
            print("Error: --observed and --expected are required for chi2", file=sys.stderr)
            sys.exit(1)
        observed = [float(x.strip()) for x in args.observed.split(",")]
        expected = [float(x.strip()) for x in args.expected.split(",")]
        result = chi2_test(observed, expected, args.alpha)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(verdict(result))

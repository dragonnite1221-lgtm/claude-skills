# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from ad_health_scorer_p1 import DEMO_CHECKS, PLATFORM_WEIGHTS, score_platform  # noqa: E402,E501
# fmt: on


def aggregate_platforms(platform_results, budgets=None):
    if not budgets:
        # Equal weight
        budgets = {p["platform"]: 1.0 / len(platform_results) for p in platform_results}
    total_budget = sum(budgets.values())
    shares = {k: v / total_budget for k, v in budgets.items()}

    aggregate = 0.0
    for pr in platform_results:
        share = shares.get(pr["platform"], 0)
        aggregate += pr["overall_score"] * share

    return {
        "aggregate_score": round(aggregate, 1),
        "budget_shares": {k: round(v, 2) for k, v in shares.items()},
        "platform_scores": {pr["platform"]: pr["overall_score"] for pr in platform_results},
    }
def print_report(result):
    print(f"Ad Health Score ({result['platform'].upper()}): {result['overall_score']}/100 (Grade: {result['grade']})")
    print(f"Checks: {result['total_checks']} — {result['passed']} pass, {result['warnings']} warn, {result['failures']} fail")
    print()
    print("Category Breakdown:")
    for cat, score in sorted(result["category_scores"].items()):
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        print(f"  {cat:25s} {bar} {score:5.1f}/100")
    print()
    if result["quick_wins"]:
        print(f"Quick Wins ({len(result['quick_wins'])}):")
        for f in result["quick_wins"]:
            print(f"  ⚡ [{f['severity'].upper()}] {f['check']}: {f['detail']}")
        print()
    if result["findings"]:
        print(f"Findings ({len(result['findings'])}):")
        for f in result["findings"]:
            detail = f" — {f['detail']}" if f["detail"] else ""
            print(f"  [{f['severity'].upper()}/{f['result'].upper()}] {f['check']}{detail}")
def main():
    p = argparse.ArgumentParser(
        description="Compute weighted 0-100 ad account health score with severity multipliers.",
        epilog="Supports Google, Meta, LinkedIn, TikTok. Run with --demo for a sample report.",
    )
    p.add_argument("--checks", help="Path to checks JSON file (array of check objects)")
    p.add_argument("--platform", choices=list(PLATFORM_WEIGHTS.keys()), default="google")
    p.add_argument("--budget", type=float, default=None, help="Monthly budget (for multi-platform weighting)")
    p.add_argument("--multi", help="Path to multi-platform JSON {platform: {checks: [...], budget: N}}")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--demo", action="store_true", help="Run with demo data")
    args = p.parse_args()

    if args.demo:
        results = []
        for platform, checks in DEMO_CHECKS.items():
            results.append(score_platform(checks, platform))
        agg = aggregate_platforms(results, {"google": 3000, "meta": 2000})

        if args.json:
            print(json.dumps({"platforms": results, "aggregate": agg}, indent=2))
        else:
            for r in results:
                print_report(r)
                print()
            print(f"Cross-Platform Aggregate: {agg['aggregate_score']}/100")
            print(f"Budget shares: {agg['budget_shares']}")
        return

    if args.multi:
        data = json.loads(Path(args.multi).read_text())
        results = []
        budgets = {}
        for platform, pdata in data.items():
            results.append(score_platform(pdata["checks"], platform))
            budgets[platform] = pdata.get("budget", 1000)
        agg = aggregate_platforms(results, budgets)
        if args.json:
            print(json.dumps({"platforms": results, "aggregate": agg}, indent=2))
        else:
            for r in results:
                print_report(r)
                print()
            print(f"Cross-Platform Aggregate: {agg['aggregate_score']}/100")
        return

    if args.checks:
        checks = json.loads(Path(args.checks).read_text())
        result = score_platform(checks, args.platform)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_report(result)
        return

    p.print_help()

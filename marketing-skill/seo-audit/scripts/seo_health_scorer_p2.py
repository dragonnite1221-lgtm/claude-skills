# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from seo_health_scorer_p1 import DEMO_CHECKS, score_checks  # noqa: E402,E501
# fmt: on


def print_report(result):
    print(f"SEO Health Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    print(f"Industry profile: {result['industry']}")
    print(f"Checks: {result['total_checks']} total — {result['passed']} pass, {result['warnings']} warn, {result['failures']} fail")
    print()

    print("Category Breakdown:")
    for cat, score in sorted(result["category_scores"].items()):
        weight = result["weights_used"].get(cat, 0)
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        print(f"  {cat:15s} {bar} {score:5.1f}/100 (weight {weight:.0%})")
    print()

    if result["quick_wins"]:
        print(f"Quick Wins ({len(result['quick_wins'])}):")
        for f in result["quick_wins"]:
            print(f"  ⚡ [{f['severity'].upper()}] {f['check']}: {f['detail']}")
        print()

    for level in ("critical", "high", "medium", "low"):
        items = result["action_plan"][level]
        if items:
            print(f"{level.upper()} ({len(items)}):")
            for f in items:
                detail = f" — {f['detail']}" if f["detail"] else ""
                print(f"  [{f['result'].upper()}] {f['check']}{detail}")
            print()
def main():
    p = argparse.ArgumentParser(
        description="Compute a weighted 0-100 SEO health score across 7 categories.",
        epilog="Run with --demo to see a sample report. Provide checks as JSON for real audits.",
    )
    p.add_argument("--checks", help="Path to checks JSON file (array of check objects)")
    p.add_argument(
        "--industry",
        choices=["saas", "ecommerce", "local", "publisher"],
        default=None,
        help="Industry profile adjusts category weights",
    )
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--demo", action="store_true", help="Run with demo data")
    args = p.parse_args()

    if args.demo:
        checks = DEMO_CHECKS
    elif args.checks:
        path = Path(args.checks)
        if not path.exists():
            print(f"[error] {path} not found", file=sys.stderr)
            sys.exit(1)
        checks = json.loads(path.read_text(encoding="utf-8"))
    else:
        p.print_help()
        sys.exit(0)

    result = score_checks(checks, industry=args.industry)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)

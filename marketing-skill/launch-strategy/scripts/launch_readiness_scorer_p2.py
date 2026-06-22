# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_readiness_scorer_base import *  # noqa: F403,E402
# fmt: off
from launch_readiness_scorer_p1 import CATEGORY_META, DEFAULT_CHECKLIST, _action_plan, _launch_decision, _score_label, score_category  # noqa: E402,E501
# fmt: on


def score_readiness(checklist: dict) -> dict:
    """Score all categories and produce an overall launch readiness result."""
    categories    = {}
    all_scores    = []
    all_blockers  = []

    for cat, items in checklist.items():
        result            = score_category(items)
        categories[cat]   = result
        all_scores.append(result["score"])
        all_blockers.extend(result["blockers"])

    overall = round(sum(all_scores) / len(all_scores)) if all_scores else 0

    return {
        "overall": {
            "score":          overall,
            "score_label":    _score_label(overall),
            "launch_decision": _launch_decision(overall, all_blockers),
            "blockers":        all_blockers,
            "generated_at":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "categories": {
            cat: {**CATEGORY_META.get(cat, {"emoji": "📋", "label": cat.title()}),
                  **res}
            for cat, res in categories.items()
        },
        "action_plan": _action_plan(categories),
    }
def pretty_print(result: dict) -> None:
    ov = result["overall"]

    print("\n" + "=" * 65)
    print("  🚀  LAUNCH READINESS SCORER")
    print("=" * 65)

    print(f"\n  Overall Score   : {ov['score']}/100  ({ov['score_label']})")
    print(f"  Launch Decision : {ov['launch_decision']}")
    if ov["blockers"]:
        print(f"\n  🚨 BLOCKERS ({len(ov['blockers'])}):")
        for b in ov["blockers"]:
            print(f"    • {b}")

    print(f"\n{'─'*65}")
    print(f"  {'CATEGORY':<30}  {'SCORE':>6}  {'DONE':>5}  {'PARTIAL':>7}  {'PENDING':>7}")
    print(f"{'─'*65}")

    for cat, res in result["categories"].items():
        bar = "█" * (res["score"] // 10) + "░" * (10 - res["score"] // 10)
        print(f"  {res['emoji']} {res['label']:<27}  {res['score']:>5}/100  "
              f"{res['items_done']:>5}  {res['items_partial']:>7}  {res['items_pending']:>7}  {bar}")

    print(f"\n{'─'*65}")
    print(f"  🗂   CATEGORY DETAILS\n")

    for cat, res in result["categories"].items():
        print(f"  {res['emoji']} {res['label']}  — {res['score']}/100  ({res['score_label']})")
        for it in res["items"]:
            icon = {"done": "✅", "partial": "🔶", "not_started": "⬜"}.get(it["status"], "⬜")
            print(f"    {icon} [{it['status']:<11}] (w={it['weight']}) {it['item']}")
        print()

    ap = result["action_plan"]
    if ap:
        print(f"  📋  ACTION PLAN  (top {len(ap)} items)\n")
        for i, a in enumerate(ap, 1):
            print(f"  {i:>2}. {a['priority']}  [{a['category']}]  {a['action']}")

    print(f"\n  Generated: {ov['generated_at']}")
    print()
def parse_args():
    parser = argparse.ArgumentParser(
        description="Score product launch readiness across categories (stdlib only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--checklist",       type=str, default=None,
                        help="Path to JSON checklist file")
    parser.add_argument("--json",            action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--export-template", action="store_true",
                        help="Print the default checklist template as JSON and exit")
    return parser.parse_args()
def main():
    args = parse_args()

    if args.export_template:
        print(json.dumps(DEFAULT_CHECKLIST, indent=2))
        return

    if args.checklist:
        with open(args.checklist) as f:
            checklist = json.load(f)
    else:
        print("🔬  DEMO MODE — using embedded sample checklist\n")
        checklist = DEFAULT_CHECKLIST

    result = score_readiness(checklist)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        pretty_print(result)

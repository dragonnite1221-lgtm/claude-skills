# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from headline_scorer_base import *  # noqa: F403,E402
# fmt: off
from headline_scorer_p1 import DEMO_HEADLINES, score_headline  # noqa: E402,E501
# fmt: on


def print_result(result: dict):
    h = result["headline"]
    score = result["overall_score"]
    grade = result["grade"]
    print(f"\n{'─' * 60}")
    print(f"  Headline: {h}")
    print(f"  Score:    {score}/100   Grade: {grade}")
    print(f"{'─' * 60}")
    bd = result["breakdown"]
    rows = [
        ("Power Words",       "power_words",        lambda r: f"found: {r['found'] or 'none'}"),
        ("Emotional Trigger", "emotional_triggers", lambda r: f"found: {r['found'] or 'none'}"),
        ("Numbers/Stats",     "numbers",            lambda r: f"found: {r['found'] or 'none'}"),
        ("Length",            "length",             lambda r: r["note"]),
        ("Specificity",       "specificity",        lambda r: f"signals: {r['signals'] or 'none'}"),
        ("Clarity",           "clarity",            lambda r: r["note"]),
    ]
    for label, key, detail_fn in rows:
        r = bd[key]
        bar_len = round(r["score"] / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        detail = detail_fn(r)
        print(f"  {label:<20} [{bar}] {r['score']:>3}/100  {detail}")
def main():
    parser = argparse.ArgumentParser(
        description="Headline scorer — rates headlines 0-100 across 6 dimensions."
    )
    parser.add_argument("headline", nargs="?", help="Single headline to score")
    parser.add_argument("--file", help="Text file with one headline per line")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.headline:
        headlines = [args.headline]
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            headlines = [line.strip() for line in f if line.strip()]
    else:
        headlines = DEMO_HEADLINES
        if not args.json:
            print("No input provided — running in demo mode.\n")
            print("Demo headlines:")
            for h in headlines:
                print(f"  • {h}")

    results = [score_headline(h) for h in headlines]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    for result in results:
        print_result(result)

    if len(results) > 1:
        avg = round(sum(r["overall_score"] for r in results) / len(results))
        best = max(results, key=lambda r: r["overall_score"])
        print(f"\n{'=' * 60}")
        print(f"  {len(results)} headlines analyzed  |  Avg score: {avg}/100")
        print(f"  Best: \"{best['headline'][:50]}\" ({best['overall_score']}/100)")
        print("=" * 60)

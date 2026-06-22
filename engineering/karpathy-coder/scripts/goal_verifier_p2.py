# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from goal_verifier_base import *  # noqa: F403,E402
# fmt: off
from goal_verifier_p1 import analyze_plan  # noqa: E402,E501
# fmt: on


def main():
    p = argparse.ArgumentParser(
        description="Check if a plan has verifiable success criteria (Karpathy Principle #4).",
        epilog="Scores each step 0-3 based on verification quality.",
    )
    p.add_argument("input", nargs="?", default="-", help="Markdown plan file, or - for stdin")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
        source = "stdin"
    else:
        path = Path(args.input)
        if not path.exists():
            print(f"[error] {path} not found", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8", errors="replace")
        source = str(path)

    result = analyze_plan(text, source)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Goal Verifier — {source}")
    print(f"Steps: {result['steps_found']}  Score: {result['score']}/{result['max_score']} ({result['percentage']}%)")
    print(f"Verdict: {result['verdict']}")
    print()

    for sr in result["step_results"]:
        icon = {"concrete": "+", "reasonable": "~", "vague": "?", "none": "!"}[sr["level"]]
        print(f"  [{icon}] {sr['title'][:100]}  ({sr['level']}, {sr['score']}/3)")

    print()
    for rec in result["recommendations"]:
        print(f"  -> {rec}")

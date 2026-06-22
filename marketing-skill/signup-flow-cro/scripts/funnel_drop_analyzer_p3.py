# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_drop_analyzer_base import *  # noqa: F403,E402
# fmt: off
from funnel_drop_analyzer_p2 import DEMO_STEPS, analyze_funnel, parse_args, pretty_print  # noqa: E402,E501
# fmt: on


def main():
    args  = parse_args()
    steps = None

    if args.stdin:
        steps = json.load(sys.stdin)
    elif args.steps:
        with open(args.steps) as f:
            steps = json.load(f)
    else:
        print("🔬  DEMO MODE — using sample SaaS signup funnel\n")
        steps = DEMO_STEPS

    result = analyze_funnel(steps)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        pretty_print(result)

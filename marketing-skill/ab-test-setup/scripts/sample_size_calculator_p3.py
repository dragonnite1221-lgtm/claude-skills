# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sample_size_calculator_base import *  # noqa: F403,E402
# fmt: off
from sample_size_calculator_p1 import add_duration, calculate_sample_size  # noqa: E402,E501
from sample_size_calculator_p2 import DEMO_SCENARIOS, parse_args, pretty_print, score_test_design  # noqa: E402,E501
# fmt: on


def main():
    args = parse_args()
    demo_mode = (args.baseline is None and args.mde is None)

    if demo_mode:
        print("🔬  DEMO MODE — running 3 sample scenarios\n")
        all_results = []
        for sc in DEMO_SCENARIOS:
            res = calculate_sample_size(sc["baseline"], sc["mde"], sc["alpha"], sc["power"])
            res = add_duration(res, sc["daily_traffic"])
            sc_score = score_test_design(res)
            res["scenario"] = sc["label"]
            res["score"] = sc_score
            all_results.append(res)
            if not args.json:
                print(f"\n{'─'*60}")
                print(f"SCENARIO: {sc['label']}")
                pretty_print(res, sc_score)

        if args.json:
            print(json.dumps(all_results, indent=2))
        return

    # Single calculation mode
    if args.baseline is None or args.mde is None:
        print("Error: --baseline and --mde are required (or omit both for demo mode).", file=sys.stderr)
        sys.exit(1)

    result = calculate_sample_size(args.baseline, args.mde, args.alpha, args.power)
    if args.daily_traffic:
        result = add_duration(result, args.daily_traffic)
    sc_score = score_test_design(result)
    result["score"] = sc_score

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        pretty_print(result, sc_score)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from humanizer_scorer_base import *  # noqa: F403,E402
# fmt: off
from humanizer_scorer_p1 import SAMPLE_AI, SAMPLE_HUMAN  # noqa: E402,E501
from humanizer_scorer_p3 import score_humanity  # noqa: E402,E501
from humanizer_scorer_p4 import print_report  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scores content 0-100 on 'humanity' by detecting AI writing patterns. "
                    "Checks AI vocabulary, sentence variance, passive voice, hedging, "
                    "em-dash overuse, and paragraph variety."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a text file to analyze. If omitted, runs demo comparing "
             "human vs AI sample content."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Also output results as JSON."
    )
    args = parser.parse_args()

    if args.file is None:
        # Demo mode: compare human vs AI sample
        print("[Demo mode — comparing human vs AI sample content]")
        print()
        print("═" * 50)
        print("SAMPLE 1: Human-written content")
        print("═" * 50)
        r1 = score_humanity(SAMPLE_HUMAN)
        print_report(r1, "Human sample")

        print("═" * 50)
        print("SAMPLE 2: AI-generated content")
        print("═" * 50)
        r2 = score_humanity(SAMPLE_AI)
        print_report(r2, "AI sample")

        print(f"  Delta: Human scored {r1['humanity_score']}, AI scored {r2['humanity_score']}")
        print(f"  Difference: {r1['humanity_score'] - r2['humanity_score']} points")
        print()
    else:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        result = score_humanity(text)
        print_report(result, args.file)

        if args.json:
            print(json.dumps(result, indent=2))

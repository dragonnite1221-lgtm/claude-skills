# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402
from customer_interview_analyzer_p0 import format_single_interview  # noqa: F401,E501


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Customer Interview Analyzer - Extracts insights, patterns, and opportunities from user interviews"
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Interview transcript text file to analyze"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    if not args.file:
        print("Usage: python customer_interview_analyzer.py <interview_file.txt>")
        print("\nThis tool analyzes customer interview transcripts to extract:")
        print("  - Pain points and frustrations")
        print("  - Feature requests and suggestions")
        print("  - Jobs to be done")
        print("  - Sentiment analysis")
        print("  - Key themes and quotes")
        sys.exit(1)

    with open(args.file, 'r') as f:
        interview_text = f.read()

    analyzer = InterviewAnalyzer()
    analysis = analyzer.analyze_interview(interview_text)

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_single_interview(analysis))

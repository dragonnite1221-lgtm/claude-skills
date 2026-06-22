# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_scorer_base import *  # noqa: F403,E402
# fmt: off
from content_scorer_p1 import SAMPLE_CONTENT, SAMPLE_KEYWORD, SAMPLE_TITLE  # noqa: E402,E501
from content_scorer_p3 import score_content  # noqa: E402,E501
from content_scorer_p4 import print_report  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scores content 0-100 on readability, SEO, structure, and engagement."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a text/markdown file to analyze. If omitted, runs demo "
             "with embedded sample content."
    )
    parser.add_argument(
        "keyword", nargs="?", default="",
        help="Target SEO keyword to check density and placement."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Also output results as JSON."
    )
    args = parser.parse_args()

    title = ""
    keyword = args.keyword
    text = ""

    if args.file is None:
        # Demo mode — use embedded sample
        print("[Demo mode — using embedded sample content]")
        text = SAMPLE_CONTENT
        title = SAMPLE_TITLE
        keyword = SAMPLE_KEYWORD
    else:
        # Read from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        # Extract title from first H1 or first line
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('Title:'):
                title = line[6:].strip()
                break
        if not title and text:
            title = text.split('\n')[0][:80]

    result = score_content(text, title, keyword)
    print_report(result, title, keyword)

    # JSON output for programmatic use
    if args.json:
        print(json.dumps(result, indent=2))

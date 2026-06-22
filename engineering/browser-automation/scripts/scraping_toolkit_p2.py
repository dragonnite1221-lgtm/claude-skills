# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scraping_toolkit_base import *  # noqa: F403,E402
# fmt: off
from scraping_toolkit_p1 import build_scraping_script  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright scraping script skeletons from URL and selectors.",
        epilog=(
            "Examples:\n"
            "  %(prog)s --url https://example.com/products --selectors '.title,.price,.rating'\n"
            "  %(prog)s --url https://example.com/search --selectors '.name,.desc' --paginate\n"
            "  %(prog)s --url https://example.com --selectors '.item' --json\n"
            "  %(prog)s --url https://example.com --selectors '.item' --output scraper.py\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to scrape",
    )
    parser.add_argument(
        "--selectors",
        required=True,
        help="Comma-separated CSS selectors for data fields (e.g. '.title,.price,.rating')",
    )
    parser.add_argument(
        "--paginate",
        action="store_true",
        default=False,
        help="Include pagination handling in generated script",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        default=False,
        help="Output JSON configuration instead of Python script",
    )

    args = parser.parse_args()

    output_format = "json" if args.json_output else "script"
    result, error = build_scraping_script(
        url=args.url,
        selectors=args.selectors,
        paginate=args.paginate,
        output_format=output_format,
    )

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)

    if args.json_output:
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result

    if args.output:
        output_path = os.path.abspath(args.output)
        with open(output_path, "w") as f:
            f.write(output_text)
        if not args.json_output:
            os.chmod(output_path, 0o755)
        print(f"Written to {output_path}", file=sys.stderr)
        sys.exit(0)
    else:
        print(output_text)
        sys.exit(0)

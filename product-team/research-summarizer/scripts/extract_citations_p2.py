# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from extract_citations_base import *  # noqa: F403,E402
# fmt: off
from extract_citations_p1 import classify_source, deduplicate, extract_author_year, extract_dois, extract_numbered_refs, extract_urls, format_apa, format_chicago, format_harvard, format_ieee  # noqa: E402,E501
# fmt: on


def format_mla(citation):
    """Format citation in MLA 9 style."""
    if citation["type"] == "doi":
        return f"doi:{citation['doi']}."
    if citation["type"] == "url":
        return f"{citation['url']}."
    if citation["type"] == "author_year":
        return f"{citation['author']}. {citation['year']}."
    if citation["type"] == "numbered":
        return citation["content"]
    return citation.get("raw", "")
FORMATTERS = {
    "apa": format_apa,
    "ieee": format_ieee,
    "chicago": format_chicago,
    "harvard": format_harvard,
    "mla": format_mla,
}
DEMO_TEXT = """
Recent studies in product management have shown significant shifts in methodology.
According to Smith & Jones (2023), agile adoption has increased by 47% since 2020.
Patel et al. (2022) found that cross-functional teams deliver 2.3x faster.

Several frameworks have been proposed:
[1] Cagan, M. Inspired: How to Create Tech Products Customers Love. Wiley, 2018.
[2] Torres, T. Continuous Discovery Habits. Product Talk LLC, 2021.
[3] Gothelf, J. & Seiden, J. Lean UX. O'Reilly Media, 2021. doi: 10.1234/leanux.2021

For further reading, see https://www.svpg.com/articles/ and the meta-analysis
by Chen (2024) on product discovery effectiveness.

Related work: doi: 10.1145/3544548.3581388
"""
def run_extraction(text, fmt, output_mode):
    """Run full extraction pipeline."""
    all_citations = []
    all_citations.extend(extract_dois(text))
    all_citations.extend(extract_author_year(text))
    all_citations.extend(extract_numbered_refs(text))
    all_citations.extend(extract_urls(text))

    citations = deduplicate(all_citations)

    for c in citations:
        c["classification"] = classify_source(c)

    formatter = FORMATTERS.get(fmt, format_apa)

    if output_mode == "json":
        result = {
            "format": fmt,
            "total": len(citations),
            "citations": [],
        }
        for i, c in enumerate(citations, 1):
            result["citations"].append({
                "index": i,
                "type": c["type"],
                "classification": c["classification"],
                "formatted": formatter(c),
                "raw": c.get("raw", ""),
            })
        print(json.dumps(result, indent=2))
    else:
        print(f"Citations ({fmt.upper()}) — {len(citations)} found\n")
        primary = [c for c in citations if c["classification"] == "primary"]
        secondary = [c for c in citations if c["classification"] == "secondary"]
        tertiary = [c for c in citations if c["classification"] == "tertiary"]

        for label, group in [("Primary Sources", primary), ("Secondary Sources", secondary), ("Tertiary Sources", tertiary)]:
            if group:
                print(f"### {label}")
                for i, c in enumerate(group, 1):
                    print(f"  {i}. {formatter(c)}")
                print()

    return citations
def main():
    parser = argparse.ArgumentParser(
        description="research-summarizer: Extract and format citations from text"
    )
    parser.add_argument("file", nargs="?", help="Input text file (omit for demo)")
    parser.add_argument(
        "--format", "-f",
        choices=["apa", "ieee", "chicago", "harvard", "mla"],
        default="apa",
        help="Citation format (default: apa)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output mode (default: text)",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read from stdin instead of file",
    )
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input file provided. Running demo...\n")
        text = DEMO_TEXT

    run_extraction(text, args.format, args.output)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_analyzer_base import *  # noqa: F403,E402
# fmt: off
from funnel_analyzer_p1 import analyze_funnel  # noqa: E402,E501
from funnel_analyzer_p2 import compare_segments, format_single_funnel_text  # noqa: E402,E501
# fmt: on


def format_text(results: Dict[str, Any]) -> str:
    """Format full results as human-readable text output."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("FUNNEL CONVERSION ANALYSIS")
    lines.append("=" * 70)

    if "stage_comparison" in results:
        # Multi-segment output
        lines.append("")
        lines.append("SEGMENT RANKINGS")
        lines.append(f"  {'Rank':>4} {'Segment':<25} {'Conversion':>12} {'Entries':>10} {'Conversions':>12}")
        lines.append(f"  {'-'*4} {'-'*25} {'-'*12} {'-'*10} {'-'*12}")
        for r in results["rankings"]:
            lines.append(
                f"  {r['rank']:>4} {r['segment']:<25} {r['overall_conversion_rate']:>11.2f}% "
                f"{r['total_entries']:>10,} {r['total_conversions']:>12,}"
            )

        lines.append("")
        for seg_name, seg_result in results["segment_results"].items():
            lines.append("")
            lines.append(format_single_funnel_text(seg_result, title=f"SEGMENT: {seg_name.upper()}"))

        # Stage comparison table
        lines.append("")
        lines.append("-" * 70)
        lines.append("STAGE-BY-STAGE COMPARISON")
        lines.append("-" * 70)
        seg_names = list(results["segment_results"].keys())
        header = f"  {'Stage':<20}"
        for sn in seg_names:
            header += f" {sn:>20}"
        lines.append(header)
        lines.append(f"  {'-'*20}" + f" {'-'*20}" * len(seg_names))

        for sc in results["stage_comparison"]:
            row = f"  {sc['stage']:<20}"
            for sn in seg_names:
                data = sc[sn]
                row += f" {data['count']:>8,} ({data['conversion_rate']:>5.1f}%)"
            lines.append(row)

    else:
        # Single funnel output
        lines.append("")
        lines.append(format_single_funnel_text(results))

    lines.append("")
    return "\n".join(lines)
def main() -> None:
    """Main entry point for the funnel analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze conversion funnels with bottleneck detection and segment comparison.",
        epilog="Example: python funnel_analyzer.py funnel_data.json --format json",
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file containing funnel data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Load input data
    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine mode: single funnel vs. segment comparison
    if "segments" in data:
        # Multi-segment mode
        stages = data.get("funnel", {}).get("stages", data.get("stages", []))
        if not stages:
            print("Error: 'stages' list required for segment comparison.", file=sys.stderr)
            sys.exit(1)
        segments = data["segments"]
        if not segments:
            print("Error: 'segments' dict is empty.", file=sys.stderr)
            sys.exit(1)
        results = compare_segments(segments, stages)
    elif "funnel" in data:
        # Single funnel mode
        funnel = data["funnel"]
        stages = funnel.get("stages", [])
        counts = funnel.get("counts", [])
        if not stages or not counts:
            print("Error: 'funnel' must contain 'stages' and 'counts' arrays.", file=sys.stderr)
            sys.exit(1)
        results = analyze_funnel(stages, counts)
    else:
        print("Error: Input must contain 'funnel' or 'segments' key.", file=sys.stderr)
        sys.exit(1)

    if args.output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))

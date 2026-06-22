# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from funnel_analyzer_base import *  # noqa: F403,E402
# fmt: off
from funnel_analyzer_p1 import analyze_funnel  # noqa: E402,E501
# fmt: on


def compare_segments(segments: Dict[str, Dict[str, Any]], stages: List[str]) -> Dict[str, Any]:
    """Compare funnel performance across segments.

    Args:
        segments: Dict mapping segment name to {"counts": [...]}.
        stages: Shared stage names for all segments.

    Returns:
        Comparison data with per-segment analysis and relative rankings.
    """
    segment_results: Dict[str, Dict[str, Any]] = {}

    for seg_name, seg_data in segments.items():
        counts = seg_data.get("counts", [])
        if len(counts) != len(stages):
            raise ValueError(
                f"Segment '{seg_name}' has {len(counts)} counts but {len(stages)} stages."
            )
        segment_results[seg_name] = analyze_funnel(stages, counts)

    # Rank segments by overall conversion rate
    ranked = sorted(
        segment_results.items(),
        key=lambda x: x[1]["overall_conversion_rate"],
        reverse=True,
    )
    rankings = [
        {
            "rank": i + 1,
            "segment": name,
            "overall_conversion_rate": result["overall_conversion_rate"],
            "total_entries": result["total_entries"],
            "total_conversions": result["total_conversions"],
        }
        for i, (name, result) in enumerate(ranked)
    ]

    # Stage-by-stage comparison
    stage_comparison: List[Dict[str, Any]] = []
    for i, stage in enumerate(stages):
        stage_data: Dict[str, Any] = {"stage": stage}
        for seg_name in segments:
            metrics = segment_results[seg_name]["stage_metrics"][i]
            stage_data[seg_name] = {
                "count": metrics["count"],
                "conversion_rate": metrics["conversion_rate"],
            }
        stage_comparison.append(stage_data)

    return {
        "segment_results": segment_results,
        "rankings": rankings,
        "stage_comparison": stage_comparison,
    }
def format_single_funnel_text(analysis: Dict[str, Any], title: str = "FUNNEL") -> str:
    """Format a single funnel analysis as human-readable text."""
    lines: List[str] = []
    lines.append(f"  {title}")
    lines.append(f"  {'='*60}")
    lines.append(f"  Total Entries:      {analysis['total_entries']:,}")
    lines.append(f"  Total Conversions:  {analysis['total_conversions']:,}")
    lines.append(f"  Total Lost:         {analysis['total_lost']:,}")
    lines.append(f"  Overall Conversion: {analysis['overall_conversion_rate']}%")
    lines.append("")

    lines.append(f"  {'Stage':<20} {'Count':>10} {'Conv Rate':>12} {'Drop-off':>12} {'Cumulative':>12}")
    lines.append(f"  {'-'*20} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")

    for m in analysis["stage_metrics"]:
        stage = m["stage"]
        count = m["count"]
        conv = f"{m['conversion_rate']:.1f}%"
        drop = f"-{m['dropoff_count']:,} ({m['dropoff_rate']:.1f}%)" if m["dropoff_count"] > 0 else "-"
        cumul = f"{m['cumulative_conversion']:.1f}%"
        lines.append(f"  {stage:<20} {count:>10,} {conv:>12} {drop:>12} {cumul:>12}")

    lines.append("")
    bn_abs = analysis["bottleneck_absolute"]
    bn_rel = analysis["bottleneck_relative"]
    lines.append(f"  BOTTLENECK (Absolute): {bn_abs['transition']} (lost {bn_abs['dropoff_count']:,})")
    lines.append(f"  BOTTLENECK (Relative): {bn_rel['transition']} ({bn_rel['dropoff_rate']}% drop-off)")

    return "\n".join(lines)

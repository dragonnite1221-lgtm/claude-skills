# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from attribution_analyzer_base import *  # noqa: F403,E402
# fmt: off
from attribution_analyzer_p1 import safe_divide  # noqa: E402,E501
# fmt: on


def format_text(results: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("MULTI-TOUCH ATTRIBUTION ANALYSIS")
    lines.append("=" * 70)

    summary = results["summary"]
    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"  Total Journeys:     {summary['total_journeys']}")
    lines.append(f"  Converted:          {summary['converted_journeys']}")
    lines.append(f"  Conversion Rate:    {summary['conversion_rate']}%")
    lines.append(f"  Total Revenue:      ${summary['total_revenue']:,.2f}")
    lines.append(f"  Channels Observed:  {', '.join(summary['channels_observed'])}")

    for model_name, credits in results["models"].items():
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"MODEL: {model_name.upper()}")
        lines.append("-" * 70)

        if not credits:
            lines.append("  No conversions to attribute.")
            continue

        total_credit = sum(credits.values())
        sorted_channels = sorted(credits.items(), key=lambda x: x[1], reverse=True)

        lines.append(f"  {'Channel':<25} {'Revenue Credit':>15} {'Share':>10}")
        lines.append(f"  {'-'*25} {'-'*15} {'-'*10}")

        for channel, credit in sorted_channels:
            pct = safe_divide(credit, total_credit) * 100
            lines.append(f"  {channel:<25} ${credit:>13,.2f} {pct:>8.1f}%")

        lines.append(f"  {'TOTAL':<25} ${total_credit:>13,.2f} {'100.0%':>10}")

    # Comparison table
    if len(results["models"]) > 1:
        lines.append("")
        lines.append("=" * 70)
        lines.append("CROSS-MODEL COMPARISON")
        lines.append("=" * 70)

        all_channels = set()
        for credits in results["models"].values():
            all_channels.update(credits.keys())
        all_channels_sorted = sorted(all_channels)

        model_names = list(results["models"].keys())
        header = f"  {'Channel':<20}"
        for mn in model_names:
            short = mn.replace("-", " ").title()
            header += f" {short:>14}"
        lines.append(header)
        lines.append(f"  {'-'*20}" + f" {'-'*14}" * len(model_names))

        for ch in all_channels_sorted:
            row = f"  {ch:<20}"
            for mn in model_names:
                val = results["models"][mn].get(ch, 0.0)
                row += f" ${val:>12,.2f}"
            lines.append(row)

    lines.append("")
    return "\n".join(lines)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from campaign_roi_calculator_base import *  # noqa: F403,E402


def format_text(results: Dict[str, Any]) -> str:
    """Format full results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("CAMPAIGN ROI ANALYSIS")
    lines.append("=" * 70)

    # Portfolio summary
    summary = results["portfolio_summary"]
    lines.append("")
    lines.append("PORTFOLIO SUMMARY")
    lines.append(f"  Total Campaigns:    {summary['total_campaigns']}")
    lines.append(f"  Total Spend:        ${summary['total_spend']:>12,.2f}")
    lines.append(f"  Total Revenue:      ${summary['total_revenue']:>12,.2f}")
    lines.append(f"  Total Profit:       ${summary['total_profit']:>12,.2f}")
    lines.append(f"  Portfolio ROI:      {summary['portfolio_roi_pct']}%")
    lines.append(f"  Portfolio ROAS:     {summary['portfolio_roas']}x")
    lines.append(f"  Blended CTR:        {summary['blended_ctr_pct']}%")
    if summary["blended_cpl"] is not None:
        lines.append(f"  Blended CPL:        ${summary['blended_cpl']:>12,.2f}")
    if summary["blended_cpa"] is not None:
        lines.append(f"  Blended CPA:        ${summary['blended_cpa']:>12,.2f}")

    if summary["top_performer"]:
        lines.append(f"  Top Performer:      {summary['top_performer']}")
    if summary["underperforming_campaigns"]:
        lines.append(f"  Flagged:            {', '.join(summary['underperforming_campaigns'])}")

    # Channel summary
    if summary["channel_summary"]:
        lines.append("")
        lines.append("-" * 70)
        lines.append("CHANNEL SUMMARY")
        lines.append(f"  {'Channel':<20} {'Spend':>12} {'Revenue':>12} {'ROI':>10} {'ROAS':>8}")
        lines.append(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
        for ch, cs in sorted(summary["channel_summary"].items()):
            lines.append(
                f"  {ch:<20} ${cs['spend']:>10,.2f} ${cs['revenue']:>10,.2f} "
                f"{cs['roi_pct']:>8.1f}% {cs['roas']:>6.2f}x"
            )

    # Individual campaigns
    for campaign in results["campaigns"]:
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"CAMPAIGN: {campaign['name']}")
        lines.append(f"Channel: {campaign['channel']}")
        lines.append("-" * 70)

        m = campaign["metrics"]
        lines.append(f"  {'Metric':<25} {'Value':>15}")
        lines.append(f"  {'-'*25} {'-'*15}")
        lines.append(f"  {'Spend':<25} ${m['spend']:>13,.2f}")
        lines.append(f"  {'Revenue':<25} ${m['revenue']:>13,.2f}")
        lines.append(f"  {'Profit':<25} ${m['profit']:>13,.2f}")
        lines.append(f"  {'ROI':<25} {m['roi_pct']:>13.2f}%")
        lines.append(f"  {'ROAS':<25} {m['roas']:>13.2f}x")

        if m["cpa"] is not None:
            lines.append(f"  {'CPA':<25} ${m['cpa']:>13,.2f}")
        if m["cpl"] is not None:
            lines.append(f"  {'CPL':<25} ${m['cpl']:>13,.2f}")
        if m["cac"] is not None:
            lines.append(f"  {'CAC':<25} ${m['cac']:>13,.2f}")
        if m["ctr_pct"] is not None:
            lines.append(f"  {'CTR':<25} {m['ctr_pct']:>13.2f}%")
        if m["cpc"] is not None:
            lines.append(f"  {'CPC':<25} ${m['cpc']:>13,.2f}")
        if m["cpm"] is not None:
            lines.append(f"  {'CPM':<25} ${m['cpm']:>13,.2f}")
        if m["cvr_pct"] is not None:
            lines.append(f"  {'Lead-to-Customer CVR':<25} {m['cvr_pct']:>13.2f}%")
        if m["lead_conversion_rate_pct"] is not None:
            lines.append(f"  {'Click-to-Lead Rate':<25} {m['lead_conversion_rate_pct']:>13.2f}%")

        # Benchmark assessments
        if campaign["assessments"]:
            lines.append("")
            lines.append("  BENCHMARK ASSESSMENT")
            for metric_name, a in campaign["assessments"].items():
                br = a["benchmark_range"]
                status = a["assessment"].upper().replace("_", " ")
                lines.append(
                    f"    {metric_name.upper()}: {a['value']} "
                    f"[low={br['low']}, target={br['target']}, high={br['high']}] "
                    f"-> {status}"
                )

        # Flags
        if campaign["flags"]:
            lines.append("")
            lines.append("  WARNING FLAGS")
            for flag in campaign["flags"]:
                lines.append(f"    ! {flag}")

        # Recommendations
        if campaign["recommendations"]:
            lines.append("")
            lines.append("  RECOMMENDATIONS")
            for i, rec in enumerate(campaign["recommendations"], 1):
                lines.append(f"    {i}. {rec}")

    lines.append("")
    return "\n".join(lines)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pipeline_analyzer_p1 import calculate_coverage_ratio, calculate_sales_velocity, calculate_stage_conversion_rates  # noqa: E402,E501
from pipeline_analyzer_p2 import analyze_deal_aging  # noqa: E402,E501
from pipeline_analyzer_p3 import assess_pipeline_risk  # noqa: E402,E501
# fmt: on


def analyze_pipeline(data: dict) -> dict[str, Any]:
    """Run complete pipeline analysis.

    Args:
        data: Pipeline data with deals, quota, stages, and average_cycle_days.

    Returns:
        Complete analysis results dictionary.
    """
    deals = data["deals"]
    quota = data["quota"]
    stages = data["stages"]
    average_cycle_days = data.get("average_cycle_days", 45)

    return {
        "coverage": calculate_coverage_ratio(deals, quota),
        "stage_conversions": calculate_stage_conversion_rates(deals, stages),
        "velocity": calculate_sales_velocity(deals),
        "aging": analyze_deal_aging(deals, average_cycle_days, stages),
        "risk": assess_pipeline_risk(deals, quota, stages),
    }
def format_currency(value: float) -> str:
    """Format a number as currency."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"
def format_text_report(results: dict) -> str:
    """Format analysis results as a human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PIPELINE ANALYSIS REPORT")
    lines.append("=" * 70)

    # Coverage
    cov = results["coverage"]
    lines.append("")
    lines.append("PIPELINE COVERAGE")
    lines.append("-" * 40)
    lines.append(f"  Total Pipeline:   {format_currency(cov['total_pipeline_value'])}")
    lines.append(f"  Quota Target:     {format_currency(cov['quota'])}")
    lines.append(f"  Coverage Ratio:   {cov['coverage_ratio']}x  (Target: {cov['target']})")
    lines.append(f"  Rating:           {cov['rating']}")

    # Stage Conversions
    lines.append("")
    lines.append("STAGE CONVERSION RATES")
    lines.append("-" * 40)
    for conv in results["stage_conversions"]:
        lines.append(
            f"  {conv['from_stage']} -> {conv['to_stage']}: "
            f"{conv['conversion_rate_pct']}% "
            f"({conv['to_count']}/{conv['from_count']})"
        )

    # Velocity
    vel = results["velocity"]
    lines.append("")
    lines.append("SALES VELOCITY")
    lines.append("-" * 40)
    lines.append(f"  Opportunities:    {vel['num_opportunities']}")
    lines.append(f"  Avg Deal Size:    {format_currency(vel['avg_deal_size'])}")
    lines.append(f"  Win Rate:         {vel['win_rate_pct']}%")
    lines.append(f"  Avg Cycle:        {vel['avg_cycle_days']} days")
    lines.append(f"  Velocity/Day:     {format_currency(vel['velocity_per_day'])}")
    lines.append(f"  Velocity/Month:   {format_currency(vel['velocity_per_month'])}")

    # Aging
    aging = results["aging"]
    lines.append("")
    lines.append("DEAL AGING ANALYSIS")
    lines.append("-" * 40)
    lines.append(f"  Total Open Deals: {aging['total_open_deals']}")
    lines.append(f"  Healthy:          {aging['healthy_deals']}")
    lines.append(f"  At Risk:          {aging['at_risk_deals']}")
    if aging["aging_deals"]:
        lines.append("")
        lines.append("  AGING DEALS (needs attention):")
        for deal in aging["aging_deals"]:
            lines.append(
                f"    - {deal['name']} ({deal['stage']}): "
                f"{deal['age_days']}d (threshold: {deal['threshold_days']}d, "
                f"+{deal['days_over']}d over) | {format_currency(deal['value'])}"
            )

    # Risk
    risk = results["risk"]
    lines.append("")
    lines.append("PIPELINE RISK ASSESSMENT")
    lines.append("-" * 40)
    lines.append(f"  Overall Risk:     {risk['overall_risk']}")
    lines.append(f"  Risk Factors:     {risk['risk_factors_count']}")

    if risk["concentration_risks"]:
        lines.append("")
        lines.append("  CONCENTRATION RISKS:")
        for cr in risk["concentration_risks"]:
            lines.append(
                f"    - {cr['name']}: {format_currency(cr['value'])} "
                f"({cr['pct_of_pipeline']}% of pipeline) [{cr['risk_level']}]"
            )

    if risk["empty_stages"]:
        lines.append("")
        lines.append(f"  EMPTY STAGES: {', '.join(risk['empty_stages'])}")

    lines.append("")
    lines.append("  STAGE DISTRIBUTION:")
    for stage, data in risk["stage_distribution"].items():
        bar = "#" * max(1, int(data["pct_of_pipeline"] / 2))
        lines.append(
            f"    {stage:20s} {data['count']:3d} deals  "
            f"{format_currency(data['value']):>10s}  "
            f"{data['pct_of_pipeline']:5.1f}%  {bar}"
        )

    if risk["coverage_gaps"]:
        lines.append("")
        lines.append("  COVERAGE GAPS BY QUARTER:")
        for gap in risk["coverage_gaps"]:
            lines.append(
                f"    - {gap['quarter']}: {gap['coverage_ratio']}x coverage "
                f"({format_currency(gap['pipeline_value'])} vs "
                f"{format_currency(gap['quarterly_target'])} target)"
            )

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)

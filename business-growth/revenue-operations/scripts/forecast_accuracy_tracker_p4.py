# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_accuracy_tracker_base import *  # noqa: F403,E402
# fmt: off
from forecast_accuracy_tracker_p1 import calculate_mape, calculate_weighted_mape, get_accuracy_rating  # noqa: E402,E501
from forecast_accuracy_tracker_p2 import analyze_bias, analyze_trend  # noqa: E402,E501
from forecast_accuracy_tracker_p3 import analyze_categories, generate_recommendations  # noqa: E402,E501
# fmt: on


def track_forecast_accuracy(data: dict) -> dict[str, Any]:
    """Run complete forecast accuracy analysis.

    Args:
        data: Forecast data with periods and optional category breakdowns.

    Returns:
        Complete forecast accuracy analysis results.
    """
    periods = data["forecast_periods"]

    mape = calculate_mape(periods)
    weighted_mape = calculate_weighted_mape(periods)
    rating = get_accuracy_rating(mape)
    bias = analyze_bias(periods)
    trend = analyze_trend(periods)

    categories = {}
    if "category_breakdowns" in data:
        categories = analyze_categories(data["category_breakdowns"])

    recommendations = generate_recommendations(mape, bias, trend, categories)

    return {
        "mape": round(mape, 1),
        "weighted_mape": round(weighted_mape, 1),
        "accuracy_rating": rating,
        "bias": bias,
        "trend": trend,
        "category_breakdowns": categories,
        "recommendations": recommendations,
        "periods_analyzed": len(periods),
    }
def format_currency(value: float) -> str:
    """Format a number as currency."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.0f}"
def format_text_report(results: dict) -> str:
    """Format analysis results as a human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("FORECAST ACCURACY REPORT")
    lines.append("=" * 70)

    # Overall accuracy
    lines.append("")
    lines.append("OVERALL ACCURACY")
    lines.append("-" * 40)
    lines.append(f"  MAPE:              {results['mape']}%")
    lines.append(f"  Weighted MAPE:     {results['weighted_mape']}%")
    lines.append(f"  Rating:            {results['accuracy_rating']['rating']}")
    lines.append(f"  Assessment:        {results['accuracy_rating']['description']}")
    lines.append(f"  Periods Analyzed:  {results['periods_analyzed']}")

    # Bias analysis
    bias = results["bias"]
    lines.append("")
    lines.append("FORECAST BIAS")
    lines.append("-" * 40)
    lines.append(f"  Direction:         {bias['direction']}")
    lines.append(f"  Bias %:            {bias['bias_pct']}%")
    lines.append(f"  Avg Bias Amount:   {format_currency(bias['avg_bias_amount'])}")
    lines.append(f"  Over-forecast:     {bias['over_forecast_count']} periods")
    lines.append(f"  Under-forecast:    {bias['under_forecast_count']} periods")
    lines.append(f"  Bias Ratio:        {bias['bias_ratio']}")

    # Trend analysis
    trend = results["trend"]
    lines.append("")
    lines.append("ACCURACY TREND")
    lines.append("-" * 40)
    lines.append(f"  Trend:             {trend['trend']}")
    lines.append(f"  Improving:         {trend['improving_periods']} periods")
    lines.append(f"  Declining:         {trend['declining_periods']} periods")
    if trend.get("early_mape") is not None and trend["trend"] != "Insufficient data":
        lines.append(f"  Early MAPE:        {trend['early_mape']}%")
        lines.append(f"  Recent MAPE:       {trend['recent_mape']}%")
        lines.append(f"  MAPE Change:       {trend['mape_change']:+.1f}%")

    if trend.get("period_errors"):
        lines.append("")
        lines.append("  PERIOD DETAIL:")
        for pe in trend["period_errors"]:
            lines.append(
                f"    {pe['period']:12s}  "
                f"Forecast: {format_currency(pe['forecast']):>10s}  "
                f"Actual: {format_currency(pe['actual']):>10s}  "
                f"Error: {pe['error_pct']}%"
            )

    # Category breakdowns
    if results["category_breakdowns"]:
        lines.append("")
        lines.append("CATEGORY BREAKDOWN")
        lines.append("-" * 40)
        for cat_name, cat_data in results["category_breakdowns"].items():
            lines.append(
                f"\n  {cat_name.upper()} (Overall MAPE: {cat_data['overall_mape']}% "
                f"- {cat_data['overall_rating']})"
            )
            for entry in cat_data["entries"]:
                lines.append(
                    f"    {entry['category']:20s}  "
                    f"Error: {entry['error_pct']:5.1f}%  "
                    f"Bias: {entry['bias']:5s}  "
                    f"Rating: {entry['rating']}"
                )

    # Recommendations
    lines.append("")
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 40)
    for i, rec in enumerate(results["recommendations"], 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)

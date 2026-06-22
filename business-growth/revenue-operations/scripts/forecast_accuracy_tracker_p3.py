# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_accuracy_tracker_base import *  # noqa: F403,E402
# fmt: off
from forecast_accuracy_tracker_p1 import calculate_mape, get_accuracy_rating  # noqa: E402,E501
# fmt: on


def analyze_categories(category_breakdowns: dict) -> dict[str, Any]:
    """Analyze accuracy by category (rep, product, segment, etc.).

    Args:
        category_breakdowns: Dict of category_name -> list of
            {category, forecast, actual} dicts.

    Returns:
        Category-level MAPE and accuracy analysis.
    """
    results = {}

    for category_name, entries in category_breakdowns.items():
        category_results = []
        for entry in entries:
            actual = entry["actual"]
            forecast = entry["forecast"]
            if actual != 0:
                error_pct = abs(actual - forecast) / abs(actual) * 100
            else:
                error_pct = 0.0

            diff = forecast - actual
            if diff > 0:
                bias = "Over"
            elif diff < 0:
                bias = "Under"
            else:
                bias = "Exact"

            rating = get_accuracy_rating(error_pct)

            category_results.append({
                "category": entry["category"],
                "forecast": forecast,
                "actual": actual,
                "error_pct": round(error_pct, 1),
                "bias": bias,
                "variance": round(diff, 2),
                "rating": rating["rating"],
            })

        # Sort by error percentage (worst first)
        category_results.sort(key=lambda x: x["error_pct"], reverse=True)

        overall_mape = calculate_mape(entries)
        results[category_name] = {
            "entries": category_results,
            "overall_mape": round(overall_mape, 1),
            "overall_rating": get_accuracy_rating(overall_mape)["rating"],
        }

    return results
def generate_recommendations(
    mape: float, bias: dict, trend: dict, categories: dict
) -> list[str]:
    """Generate actionable recommendations based on analysis results.

    Args:
        mape: Overall MAPE percentage.
        bias: Bias analysis results.
        trend: Trend analysis results.
        categories: Category analysis results.

    Returns:
        List of recommendation strings.
    """
    recommendations = []

    # MAPE-based recommendations
    if mape > 25:
        recommendations.append(
            "CRITICAL: MAPE exceeds 25%. Implement structured forecasting methodology "
            "(e.g., weighted pipeline with stage-based probabilities)."
        )
    elif mape > 15:
        recommendations.append(
            "Forecast accuracy needs improvement. Consider implementing deal-level "
            "forecasting with commit/upside/pipeline categories."
        )

    # Bias-based recommendations
    if bias["direction"] == "Over-forecasting" and abs(bias["bias_pct"]) > 10:
        recommendations.append(
            f"Systematic over-forecasting detected ({bias['bias_pct']}% bias). "
            "Review deal qualification criteria and apply more conservative "
            "stage probabilities."
        )
    elif bias["direction"] == "Under-forecasting" and abs(bias["bias_pct"]) > 10:
        recommendations.append(
            f"Systematic under-forecasting detected ({bias['bias_pct']}% bias). "
            "Review upside deals more carefully and improve pipeline visibility."
        )

    # Trend-based recommendations
    if trend["trend"] == "Declining":
        recommendations.append(
            "Forecast accuracy is declining over time. Schedule a forecasting "
            "methodology review and retrain the team on forecasting best practices."
        )
    elif trend["trend"] == "Improving":
        recommendations.append(
            "Forecast accuracy is improving. Continue current methodology and "
            "document best practices for consistency."
        )

    # Category-based recommendations
    for cat_name, cat_data in categories.items():
        worst_entries = [
            e for e in cat_data["entries"] if e["error_pct"] > 25
        ]
        if worst_entries:
            names = ", ".join(e["category"] for e in worst_entries[:3])
            recommendations.append(
                f"High error rates in {cat_name}: {names}. "
                f"Provide targeted coaching on forecasting discipline."
            )

    if not recommendations:
        recommendations.append(
            "Forecasting performance is strong. Maintain current processes "
            "and continue monitoring for drift."
        )

    return recommendations

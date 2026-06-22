# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import FEATURE_LABELS  # noqa: E402,E501
# fmt: on


def identify_differentiators(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify features where our product leads all competitors.

    Args:
        comparison: Comparison matrix data.

    Returns:
        List of differentiator features with details.
    """
    differentiators = []
    for entry in comparison["matrix"]:
        if entry["we_lead"] and entry["our_score"] >= 2:
            # Calculate gap from nearest competitor
            competitor_scores = [
                entry["scores"][c] for c in comparison["competitors"]
            ]
            max_competitor = max(competitor_scores) if competitor_scores else 0
            gap = entry["our_score"] - max_competitor

            differentiators.append({
                "feature": entry["feature"],
                "category": entry["category"],
                "our_score": entry["our_score"],
                "our_label": FEATURE_LABELS.get(entry["our_score"], "Unknown"),
                "best_competitor_score": max_competitor,
                "gap": gap,
            })

    # Sort by gap size descending
    differentiators.sort(key=lambda d: d["gap"], reverse=True)
    return differentiators
def identify_vulnerabilities(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify features where competitors lead our product.

    Args:
        comparison: Comparison matrix data.

    Returns:
        List of vulnerability features with details.
    """
    vulnerabilities = []
    for entry in comparison["matrix"]:
        if entry["we_trail"]:
            # Find which competitor leads
            leader_scores = {
                p: entry["scores"][p]
                for p in comparison["competitors"]
                if entry["scores"][p] == entry["max_score"]
            }
            gap = entry["max_score"] - entry["our_score"]

            vulnerabilities.append({
                "feature": entry["feature"],
                "category": entry["category"],
                "our_score": entry["our_score"],
                "our_label": FEATURE_LABELS.get(entry["our_score"], "Unknown"),
                "leading_competitors": leader_scores,
                "gap": gap,
            })

    # Sort by gap size descending
    vulnerabilities.sort(key=lambda v: v["gap"], reverse=True)
    return vulnerabilities
def generate_win_themes(
    differentiators: list[dict[str, Any]],
    competitive_scores: dict[str, dict[str, Any]],
    our_product: str,
) -> list[str]:
    """Generate win themes based on differentiators and competitive position.

    Args:
        differentiators: List of differentiator features.
        competitive_scores: Product competitive scores.
        our_product: Our product name.

    Returns:
        List of win theme strings.
    """
    themes = []

    # Theme from top differentiators
    if differentiators:
        top_diff_categories = list({d["category"] for d in differentiators[:5]})
        for cat in top_diff_categories[:3]:
            cat_diffs = [d for d in differentiators if d["category"] == cat]
            feature_names = [d["feature"] for d in cat_diffs[:3]]
            themes.append(
                f"Superior {cat} capabilities: {', '.join(feature_names)}"
            )

    # Theme from overall competitive position
    our_score = competitive_scores.get(our_product, {}).get("weighted_score", 0)
    competitor_scores = [
        (p, s["weighted_score"])
        for p, s in competitive_scores.items()
        if p != our_product
    ]
    if competitor_scores:
        best_competitor_name, best_competitor_score = max(
            competitor_scores, key=lambda x: x[1]
        )
        if our_score > best_competitor_score:
            themes.append(
                f"Overall strongest solution ({our_score:.1f}% vs {best_competitor_name} at {best_competitor_score:.1f}%)"
            )

    # Theme from breadth of coverage
    strong_diffs = [d for d in differentiators if d["gap"] >= 2]
    if len(strong_diffs) >= 3:
        themes.append(
            f"Clear technical leadership across {len(strong_diffs)} key features with significant competitive gaps"
        )

    if not themes:
        themes.append("Competitive parity - emphasize implementation quality, support, and total cost of ownership")

    return themes

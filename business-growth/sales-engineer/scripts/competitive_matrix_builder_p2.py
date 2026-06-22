# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import normalize_score, safe_divide  # noqa: E402,E501
# fmt: on


def build_comparison_matrix(data: dict[str, Any]) -> dict[str, Any]:
    """Build the feature comparison matrix from input data.

    Args:
        data: Competitive data with categories, features, and scores.

    Returns:
        Comparison matrix with per-feature and per-category scores.
    """
    our_product = data["our_product"]
    competitors = data["competitors"]
    all_products = [our_product] + competitors

    matrix: list[dict[str, Any]] = []
    category_summaries: dict[str, dict[str, Any]] = {}

    for category in data["categories"]:
        cat_name = category["name"]
        cat_weight = category.get("weight", 1.0)
        cat_features = category.get("features", [])

        cat_scores: dict[str, list[int]] = {p: [] for p in all_products}

        for feature in cat_features:
            feature_name = feature["name"]
            scores: dict[str, int] = {}

            for product in all_products:
                raw_score = feature.get("scores", {}).get(product, 0)
                scores[product] = normalize_score(raw_score)
                cat_scores[product].append(scores[product])

            # Determine leader for this feature
            max_score = max(scores.values())
            leaders = [p for p, s in scores.items() if s == max_score]

            matrix.append({
                "category": cat_name,
                "feature": feature_name,
                "scores": scores,
                "leaders": leaders,
                "our_score": scores[our_product],
                "max_score": max_score,
                "we_lead": our_product in leaders and len(leaders) == 1,
                "we_trail": scores[our_product] < max_score,
            })

        # Category summary
        cat_product_scores = {}
        for product in all_products:
            product_scores = cat_scores[product]
            total = sum(product_scores)
            max_possible = len(product_scores) * 3
            pct = safe_divide(total, max_possible) * 100
            cat_product_scores[product] = {
                "total_score": total,
                "max_possible": max_possible,
                "percentage": round(pct, 1),
            }

        category_summaries[cat_name] = {
            "weight": cat_weight,
            "feature_count": len(cat_features),
            "product_scores": cat_product_scores,
        }

    return {
        "our_product": our_product,
        "competitors": competitors,
        "all_products": all_products,
        "matrix": matrix,
        "category_summaries": category_summaries,
    }
def compute_competitive_scores(
    comparison: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Compute weighted competitive scores for each product.

    Args:
        comparison: Comparison matrix data.

    Returns:
        Product scores with weighted and unweighted totals.
    """
    all_products = comparison["all_products"]
    category_summaries = comparison["category_summaries"]

    product_scores: dict[str, dict[str, float]] = {
        p: {"weighted_total": 0.0, "max_weighted": 0.0, "unweighted_total": 0, "max_unweighted": 0}
        for p in all_products
    }

    for cat_name, cat_data in category_summaries.items():
        weight = cat_data["weight"]
        for product in all_products:
            p_data = cat_data["product_scores"][product]
            product_scores[product]["weighted_total"] += p_data["total_score"] * weight
            product_scores[product]["max_weighted"] += p_data["max_possible"] * weight
            product_scores[product]["unweighted_total"] += p_data["total_score"]
            product_scores[product]["max_unweighted"] += p_data["max_possible"]

    result = {}
    for product in all_products:
        ps = product_scores[product]
        weighted_pct = safe_divide(ps["weighted_total"], ps["max_weighted"]) * 100
        unweighted_pct = safe_divide(ps["unweighted_total"], ps["max_unweighted"]) * 100
        result[product] = {
            "weighted_score": round(weighted_pct, 1),
            "unweighted_score": round(unweighted_pct, 1),
            "weighted_total": round(ps["weighted_total"], 2),
            "max_weighted": round(ps["max_weighted"], 2),
        }

    return result

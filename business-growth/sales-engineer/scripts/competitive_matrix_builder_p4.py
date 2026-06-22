# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p2 import build_comparison_matrix, compute_competitive_scores  # noqa: E402,E501
from competitive_matrix_builder_p3 import generate_win_themes, identify_differentiators, identify_vulnerabilities  # noqa: E402,E501
# fmt: on


def analyze_competitive(data: dict[str, Any]) -> dict[str, Any]:
    """Run the complete competitive analysis pipeline.

    Args:
        data: Parsed competitive data dictionary.

    Returns:
        Complete analysis results dictionary.
    """
    comparison = build_comparison_matrix(data)
    competitive_scores = compute_competitive_scores(comparison)
    differentiators = identify_differentiators(comparison)
    vulnerabilities = identify_vulnerabilities(comparison)
    win_themes = generate_win_themes(
        differentiators, competitive_scores, comparison["our_product"]
    )

    return {
        "analysis_info": {
            "our_product": comparison["our_product"],
            "competitors": comparison["competitors"],
            "total_features": len(comparison["matrix"]),
            "total_categories": len(comparison["category_summaries"]),
        },
        "competitive_scores": competitive_scores,
        "category_breakdown": comparison["category_summaries"],
        "comparison_matrix": comparison["matrix"],
        "differentiators": differentiators,
        "vulnerabilities": vulnerabilities,
        "win_themes": win_themes,
    }

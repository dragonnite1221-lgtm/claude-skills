# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import FEATURE_LABELS  # noqa: E402,E501
# fmt: on


def format_text(result: dict[str, Any]) -> str:
    """Format analysis results as human-readable text.

    Args:
        result: Complete analysis results dictionary.

    Returns:
        Formatted text string.
    """
    lines = []
    info = result["analysis_info"]
    all_products = [info["our_product"]] + info["competitors"]

    lines.append("=" * 80)
    lines.append("COMPETITIVE MATRIX ANALYSIS")
    lines.append("=" * 80)
    lines.append(f"Our Product:   {info['our_product']}")
    lines.append(f"Competitors:   {', '.join(info['competitors'])}")
    lines.append(f"Features:      {info['total_features']}")
    lines.append(f"Categories:    {info['total_categories']}")
    lines.append("")

    # Competitive scores
    lines.append("-" * 80)
    lines.append("COMPETITIVE SCORES")
    lines.append("-" * 80)
    lines.append(f"{'Product':<25} {'Weighted':>10} {'Unweighted':>12}")
    lines.append("-" * 80)

    # Sort by weighted score descending
    sorted_scores = sorted(
        result["competitive_scores"].items(),
        key=lambda x: x[1]["weighted_score"],
        reverse=True,
    )
    for product, scores in sorted_scores:
        marker = " <-- US" if product == info["our_product"] else ""
        lines.append(
            f"{product:<25} {scores['weighted_score']:>9.1f}% {scores['unweighted_score']:>11.1f}%{marker}"
        )
    lines.append("")

    # Feature matrix
    lines.append("-" * 80)
    lines.append("FEATURE COMPARISON MATRIX")
    lines.append("-" * 80)

    # Build header
    product_cols = "  ".join(f"{p[:10]:>10}" for p in all_products)
    lines.append(f"{'Feature':<30} {product_cols}")
    lines.append("-" * 80)

    current_category = ""
    for entry in result["comparison_matrix"]:
        if entry["category"] != current_category:
            current_category = entry["category"]
            cat_data = result["category_breakdown"].get(current_category, {})
            weight = cat_data.get("weight", 1.0)
            lines.append(f"\n  [{current_category}] (weight: {weight}x)")

        score_cols = "  ".join(
            f"{FEATURE_LABELS.get(entry['scores'].get(p, 0), 'N/A'):>10}"
            for p in all_products
        )
        lead_marker = " *" if entry["we_lead"] else (" !" if entry["we_trail"] else "")
        feature_display = entry["feature"][:28]
        lines.append(f"    {feature_display:<28} {score_cols}{lead_marker}")
    lines.append("")
    lines.append("  * = We lead  |  ! = We trail")
    lines.append("")

    # Differentiators
    diffs = result["differentiators"]
    if diffs:
        lines.append("-" * 80)
        lines.append(f"DIFFERENTIATORS ({len(diffs)} features where we lead)")
        lines.append("-" * 80)
        for d in diffs:
            lines.append(
                f"  + {d['feature']} [{d['category']}] "
                f"- Us: {d['our_label']} vs Best Competitor: {FEATURE_LABELS.get(d['best_competitor_score'], 'N/A')} "
                f"(gap: +{d['gap']})"
            )
        lines.append("")

    # Vulnerabilities
    vulns = result["vulnerabilities"]
    if vulns:
        lines.append("-" * 80)
        lines.append(f"VULNERABILITIES ({len(vulns)} features where competitors lead)")
        lines.append("-" * 80)
        for v in vulns:
            leaders = ", ".join(
                f"{p}: {FEATURE_LABELS.get(s, 'N/A')}"
                for p, s in v["leading_competitors"].items()
            )
            lines.append(
                f"  - {v['feature']} [{v['category']}] "
                f"- Us: {v['our_label']} vs {leaders} "
                f"(gap: -{v['gap']})"
            )
        lines.append("")

    # Win themes
    themes = result["win_themes"]
    lines.append("-" * 80)
    lines.append("WIN THEMES")
    lines.append("-" * 80)
    for i, theme in enumerate(themes, 1):
        lines.append(f"  {i}. {theme}")
    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)

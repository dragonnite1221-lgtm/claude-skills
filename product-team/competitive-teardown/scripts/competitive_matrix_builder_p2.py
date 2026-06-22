# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import calculate_weighted_scores, gap_analysis, positioning_analysis  # noqa: E402,E501
# fmt: on


def format_text(result: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("COMPETITIVE MATRIX ANALYSIS")
    lines.append(f"Generated: {result['generated_at']}")
    lines.append("=" * 70)

    # Ranking table
    lines.append("\n## COMPETITIVE RANKING\n")
    lines.append(f"{'Rank':<6}{'Competitor':<25}{'Score':<10}{'Tier':<20}")
    lines.append("-" * 61)
    for i, c in enumerate(result["scored_competitors"], 1):
        marker = " ← YOU" if c.get("is_you") else ""
        lines.append(f"{i:<6}{c['name']:<25}{c['overall_score']:<10}{c['tier']:<20}{marker}")

    # Dimension breakdown
    lines.append("\n## DIMENSION BREAKDOWN\n")
    dims = result["dimensions"]
    header = f"{'Dimension':<20}" + "".join(f"{c['name'][:12]:<14}" for c in result["scored_competitors"])
    lines.append(header)
    lines.append("-" * len(header))
    for dim in dims:
        row = f"{dim:<20}"
        for c in result["scored_competitors"]:
            val = c["dimensions"].get(dim, {}).get("raw", "N/A")
            row += f"{val:<14}"
        lines.append(row)

    # Gap analysis
    if result.get("gap_analysis"):
        ga = result["gap_analysis"]
        if ga["biggest_opportunities"]:
            lines.append("\n## BIGGEST OPPORTUNITIES (where you're behind)\n")
            for opp in ga["biggest_opportunities"]:
                lines.append(f"  • {opp['dimension']}: You={opp['your_score']}, "
                           f"Best={opp['competitor_best']}, Gap={opp['gap_to_best']} "
                           f"[{opp['priority'].upper()} priority]")

        if ga["competitive_advantages"]:
            lines.append("\n## COMPETITIVE ADVANTAGES (where you lead)\n")
            for adv in ga["competitive_advantages"]:
                lines.append(f"  • {adv['dimension']}: You={adv['your_score']}, "
                           f"Avg={adv['competitor_avg']}, Lead=+{adv['gap_to_avg']}")

    # Positioning
    pos = result.get("positioning", {})
    if pos:
        lines.append("\n## MARKET POSITIONING\n")
        lines.append(f"  Market Leaders: {', '.join(pos.get('market_leaders', ['None']))}")
        if pos.get("your_rank"):
            lines.append(f"  Your Rank: #{pos['your_rank']} of {pos['total_competitors']}")
        dist = pos.get("score_distribution", {})
        lines.append(f"  Score Range: {dist.get('min', 0)} - {dist.get('max', 0)} "
                    f"(avg: {dist.get('mean', 0)}, stdev: {dist.get('stdev', 0)})")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
def build_matrix(data: Dict[str, Any], weight_overrides: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Main entry: build competitive matrix from input data."""
    competitors = data.get("competitors", [])
    dimensions = data.get("dimensions", [])
    your_product = data.get("your_product", {})

    if not competitors:
        return {"error": "No competitors provided"}
    if not dimensions:
        # Auto-detect from first competitor's scores
        dimensions = list(competitors[0].get("scores", {}).keys())

    weights = data.get("weights", {})
    if weight_overrides:
        weights.update(weight_overrides)

    # Include your product in scoring if provided
    all_entries = list(competitors)
    if your_product:
        your_product["is_you"] = True
        all_entries.insert(0, your_product)

    scored = calculate_weighted_scores(all_entries, dimensions, weights)

    # Mark your product
    for s in scored:
        if any(c.get("is_you") and c["name"] == s["name"] for c in all_entries):
            s["is_you"] = True

    result = {
        "generated_at": datetime.now().isoformat(),
        "dimensions": dimensions,
        "weights": weights if weights else {d: 1.0 for d in dimensions},
        "scored_competitors": scored,
        "positioning": positioning_analysis(scored)
    }

    if your_product:
        result["gap_analysis"] = gap_analysis(
            your_product.get("scores", {}), scored, dimensions
        )

    return result
def parse_weights(weight_str: str) -> Dict[str, float]:
    """Parse weight string like 'pricing=2,ux=1.5' into dict."""
    weights = {}
    for pair in weight_str.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            weights[k.strip()] = float(v.strip())
    return weights

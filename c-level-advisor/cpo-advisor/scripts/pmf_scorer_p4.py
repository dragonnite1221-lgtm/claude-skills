# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pmf_scorer_base import *  # noqa: F403,E402
# fmt: off
from pmf_scorer_p1 import DIMENSION_WEIGHTS  # noqa: E402,E501
from pmf_scorer_p3 import pmf_status  # noqa: E402,E501
# fmt: on


def top_recommendations(dim_scores: dict, data: dict) -> list[str]:
    """Prioritized recommendations based on weakest dimensions."""
    recs = []
    model = data.get("business_model", "b2b_saas")

    ranked = sorted(dim_scores.items(), key=lambda x: x[1])

    for dim, score in ranked:
        if score < 0.40:
            if dim == "retention":
                recs.append(
                    "CRITICAL — Retention: Run cohort analysis by segment. Find the cohort with highest D30. "
                    "Interview 10 of those users. Build for them exclusively until retention flattens."
                )
            elif dim == "engagement":
                recs.append(
                    "Engagement: Define your 'aha moment' — the one action that predicts long-term retention. "
                    "Measure time-to-aha. Remove every friction point on that path."
                )
            elif dim == "satisfaction":
                recs.append(
                    "Satisfaction: Run Sean Ellis survey immediately (need n ≥ 40). "
                    "Interview every 'somewhat disappointed' user — the gap between 'somewhat' and 'very' is your product gap."
                )
            elif dim == "growth":
                recs.append(
                    "Growth: Track signup source for every new user. If organic < 20%, "
                    "you may be papering over weak PMF with paid acquisition. Fix retention first."
                )

    if not recs:
        recs.append(
            "All dimensions scoring above threshold. Focus: "
            "(1) Defend moat, (2) Expand ICP carefully, (3) Build referral flywheel."
        )

    if model == "b2b_saas":
        recs.append("B2B tip: Track NRR (Net Revenue Retention). PMF in B2B requires expansion, not just retention.")
    elif model == "consumer":
        recs.append("Consumer tip: Find your D7 'magic moment'. The habit window is small — optimize for it.")
    elif model == "plg":
        recs.append("PLG tip: Define your PQL (product-qualified lead). The activation event that predicts paid conversion.")
    elif model == "marketplace":
        recs.append("Marketplace tip: Measure both sides separately. PMF on demand side ≠ PMF on supply side.")

    return recs
def render_report(data: dict, dim_scores: dict, dim_findings: dict, overall: float) -> str:
    status, description = pmf_status(overall)
    recs = top_recommendations(dim_scores, data)

    lines = []
    lines.append("=" * 60)
    lines.append(f"  PMF SCORER — {data.get('product_name', 'Product')}")
    lines.append(f"  Model: {data.get('business_model', 'unknown').upper()}")
    lines.append("=" * 60)
    lines.append("")

    # Overall
    bar_len = 40
    filled = round(overall * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    lines.append(f"  Overall PMF Score: {overall:.0%}")
    lines.append(f"  [{bar}]")
    lines.append(f"  Status: {status}")
    lines.append(f"  {description}")
    lines.append("")

    # Dimension breakdown
    lines.append("  DIMENSION SCORES")
    lines.append("  " + "-" * 50)
    for dim, weight in DIMENSION_WEIGHTS.items():
        score = dim_scores.get(dim, 0.0)
        dim_bar_len = 20
        dim_filled = round(score * dim_bar_len)
        dim_bar = "█" * dim_filled + "░" * (dim_bar_len - dim_filled)
        label = dim.capitalize().ljust(12)
        lines.append(f"  {label} [{dim_bar}] {score:.0%}  (weight: {weight:.0%})")
    lines.append("")

    # Findings per dimension
    for dim in ["retention", "engagement", "satisfaction", "growth"]:
        findings = dim_findings.get(dim, [])
        if findings:
            lines.append(f"  {dim.upper()} FINDINGS")
            for f in findings:
                lines.append(f"    {f}")
            lines.append("")

    # Recommendations
    lines.append("  PRIORITIZED RECOMMENDATIONS")
    lines.append("  " + "-" * 50)
    for i, rec in enumerate(recs, 1):
        # Wrap at 70 chars
        words = rec.split()
        line = f"  {i}. "
        for word in words:
            if len(line) + len(word) + 1 > 72:
                lines.append(line)
                line = "     " + word + " "
            else:
                line += word + " "
        lines.append(line.rstrip())
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)

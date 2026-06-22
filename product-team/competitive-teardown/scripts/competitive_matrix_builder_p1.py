# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402


def load_competitors(path: str) -> Dict[str, Any]:
    """Load competitor data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)
def normalize_score(value: float, min_val: float = 1.0, max_val: float = 10.0) -> float:
    """Normalize a score to 0-100 scale."""
    return max(0.0, min(100.0, ((value - min_val) / (max_val - min_val)) * 100))
def classify_tier(score: float) -> str:
    """Classify competitor into tier based on overall score."""
    if score >= 80:
        return "Leader"
    elif score >= 60:
        return "Strong Competitor"
    elif score >= 40:
        return "Viable Alternative"
    elif score >= 20:
        return "Niche Player"
    else:
        return "Weak"
def calculate_weighted_scores(
    competitors: List[Dict[str, Any]],
    dimensions: List[str],
    weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """Calculate weighted scores for each competitor across dimensions."""
    if weights is None:
        weights = {d: 1.0 for d in dimensions}

    results = []
    for comp in competitors:
        scores = comp.get("scores", {})
        weighted_total = 0.0
        weight_sum = 0.0
        dimension_results = {}

        for dim in dimensions:
            raw = scores.get(dim, 0)
            w = weights.get(dim, 1.0)
            normalized = normalize_score(raw)
            weighted = normalized * w
            weighted_total += weighted
            weight_sum += w
            dimension_results[dim] = {
                "raw": raw,
                "normalized": round(normalized, 1),
                "weight": w,
                "weighted": round(weighted, 1)
            }

        overall = round(weighted_total / weight_sum, 1) if weight_sum > 0 else 0
        results.append({
            "name": comp["name"],
            "overall_score": overall,
            "dimensions": dimension_results,
            "tier": classify_tier(overall),
            "pricing": comp.get("pricing", {}),
            "strengths": comp.get("strengths", []),
            "weaknesses": comp.get("weaknesses", [])
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results
def gap_analysis(
    your_scores: Dict[str, float],
    competitor_scores: List[Dict[str, Any]],
    dimensions: List[str]
) -> Dict[str, Any]:
    """Identify gaps between your product and competitors."""
    gaps = {}
    for dim in dimensions:
        your_val = your_scores.get(dim, 0)
        comp_vals = [c["dimensions"][dim]["raw"] for c in competitor_scores if dim in c.get("dimensions", {})]
        if not comp_vals:
            continue

        avg_comp = mean(comp_vals)
        best_comp = max(comp_vals)
        gap_to_avg = round(your_val - avg_comp, 1)
        gap_to_best = round(your_val - best_comp, 1)

        gaps[dim] = {
            "your_score": your_val,
            "competitor_avg": round(avg_comp, 1),
            "competitor_best": best_comp,
            "gap_to_avg": gap_to_avg,
            "gap_to_best": gap_to_best,
            "status": "ahead" if gap_to_avg > 0.5 else ("behind" if gap_to_avg < -0.5 else "parity"),
            "priority": "high" if gap_to_best < -2 else ("medium" if gap_to_best < -1 else "low")
        }

    return {
        "gaps": gaps,
        "biggest_opportunities": sorted(
            [{"dimension": k, **v} for k, v in gaps.items() if v["status"] == "behind"],
            key=lambda x: x["gap_to_best"]
        )[:5],
        "competitive_advantages": sorted(
            [{"dimension": k, **v} for k, v in gaps.items() if v["status"] == "ahead"],
            key=lambda x: -x["gap_to_avg"]
        )[:5]
    }
def positioning_analysis(scored: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate positioning insights from scored competitors."""
    scores = [c["overall_score"] for c in scored]
    return {
        "market_leaders": [c["name"] for c in scored if c["tier"] == "Leader"],
        "your_rank": next((i + 1 for i, c in enumerate(scored) if c.get("is_you")), None),
        "total_competitors": len(scored),
        "score_distribution": {
            "mean": round(mean(scores), 1) if scores else 0,
            "stdev": round(stdev(scores), 1) if len(scores) > 1 else 0,
            "min": round(min(scores), 1) if scores else 0,
            "max": round(max(scores), 1) if scores else 0
        },
        "tier_distribution": {
            tier: len([c for c in scored if c["tier"] == tier])
            for tier in ["Leader", "Strong Competitor", "Viable Alternative", "Niche Player", "Weak"]
        }
    }

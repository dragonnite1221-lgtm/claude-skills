# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_matrix_scorer_base import *  # noqa: F403,E402


def normalize_weights(criteria: List[Dict]) -> List[Dict]:
    """Ensure weights sum to 1.0."""
    total = sum(c["weight"] for c in criteria)
    if abs(total - 1.0) > 0.001:
        for c in criteria:
            c["weight"] = c["weight"] / total
    return criteria
def score_option(option: Dict, criteria: List[Dict]) -> float:
    """Calculate weighted score for an option."""
    total = 0.0
    for c in criteria:
        score = option["scores"].get(c["name"], 5)  # Default to 5 if missing
        total += score * c["weight"]
    return round(total, 3)
def score_all(options: List[Dict], criteria: List[Dict]) -> List[Tuple[str, float]]:
    """Return sorted list of (option_name, weighted_score)."""
    results = []
    for opt in options:
        s = score_option(opt, criteria)
        results.append((opt["name"], s))
    return sorted(results, key=lambda x: x[1], reverse=True)
def sensitivity_analysis(options: List[Dict], criteria: List[Dict]) -> Dict:
    """
    Test how result changes when each criterion's weight is varied ±30%.
    Returns dict: criterion → {stable: bool, risk_of_flip: bool, details: str}
    """
    baseline = score_all(options, criteria)
    winner = baseline[0][0]
    results = {}

    for i, c in enumerate(criteria):
        flips = []
        for delta in [-0.30, -0.20, -0.10, +0.10, +0.20, +0.30]:
            # Adjust weight of criterion i, redistribute remainder proportionally
            test_criteria = [dict(cr) for cr in criteria]
            new_weight = max(0.01, test_criteria[i]["weight"] + delta)
            old_weight = test_criteria[i]["weight"]
            diff = new_weight - old_weight
            
            # Redistribute diff across other criteria
            others = [j for j in range(len(test_criteria)) if j != i]
            total_other = sum(test_criteria[j]["weight"] for j in others)
            
            if total_other > 0:
                for j in others:
                    proportion = test_criteria[j]["weight"] / total_other
                    test_criteria[j]["weight"] -= diff * proportion
                    test_criteria[j]["weight"] = max(0.01, test_criteria[j]["weight"])
            
            test_criteria[i]["weight"] = new_weight
            test_criteria = normalize_weights(test_criteria)
            
            test_results = score_all(options, test_criteria)
            if test_results[0][0] != winner:
                flips.append((delta, test_results[0][0]))
        
        if flips:
            smallest_delta = min(abs(delta) for delta, _name in flips)
            results[c["name"]] = {
                "stable": False,
                "flip_at": f"±{int(smallest_delta*100)}% weight change",
                "flip_to": flips[0][1],
                "importance": "HIGH — result depends heavily on this weight"
            }
        else:
            results[c["name"]] = {
                "stable": True,
                "flip_at": None,
                "flip_to": None,
                "importance": "LOW — winner holds even with significant weight changes"
            }
    
    return results
def close_call_analysis(results: List[Tuple[str, float]]) -> List[Dict]:
    """Find options within 10% of winner score — these are close calls."""
    if not results:
        return []
    winner_score = results[0][1]
    close = []
    for name, score in results[1:]:
        gap = winner_score - score
        gap_pct = (gap / winner_score * 100) if winner_score > 0 else 0
        if gap_pct <= 15:
            close.append({
                "name": name,
                "score": score,
                "gap": round(gap, 3),
                "gap_pct": round(gap_pct, 1),
                "verdict": "Very close — recheck assumptions" if gap_pct <= 5 else "Close — worth a second look"
            })
    return close
def criterion_breakdown(options: List[Dict], criteria: List[Dict]) -> Dict:
    """Show per-criterion scores for each option."""
    breakdown = {}
    for opt in options:
        breakdown[opt["name"]] = {}
        for c in criteria:
            raw = opt["scores"].get(c["name"], 5)
            weighted = raw * c["weight"]
            breakdown[opt["name"]][c["name"]] = {
                "raw": raw,
                "weighted": round(weighted, 3),
                "weight": f"{round(c['weight']*100)}%"
            }
    return breakdown
def hr(char="─", width=65):
    return char * width

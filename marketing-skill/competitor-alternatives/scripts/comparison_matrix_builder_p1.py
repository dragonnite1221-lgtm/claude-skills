# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comparison_matrix_builder_base import *  # noqa: F403,E402


STATUS_SCORE = {
    "full":    2,
    "partial": 1,
    "no":      0,
    "planned": 0,  # planned ≠ shipped; conservative scoring
}
STATUS_LABEL = {
    "full":    "✅",
    "partial": "🔶",
    "no":      "❌",
    "planned": "🗓",
}
STATUS_TEXT = {
    "full":    "Full",
    "partial": "Partial",
    "no":      "No",
    "planned": "Planned",
}
FEATURE_IMPORTANCE = {
    # Generic defaults — override per-feature with "weight" in JSON
    "default": 1,
}
def normalise_status(s: str) -> str:
    s = (s or "no").strip().lower()
    return s if s in STATUS_SCORE else "no"
def _verdict(win_pct: int) -> str:
    if win_pct >= 70: return "Strong advantage"
    if win_pct >= 50: return "Slight advantage"
    if win_pct >= 35: return "Competitive parity"
    return "Trailing"
def build_matrix(data: dict) -> dict:
    your_product = data.get("your_product", "Your Product")
    features     = data.get("features", [])

    if not features:
        raise ValueError("No features provided in input.")

    # Collect competitor names (ordered, deduplicated)
    competitors = []
    seen        = set()
    for f in features:
        for c in f.get("competitors", {}):
            if c not in seen:
                competitors.append(c)
                seen.add(c)

    categories = sorted(set(f.get("category", "General") for f in features))

    # --- per-feature analysis ---
    feature_rows = []
    for f in features:
        fname     = f.get("name", "?")
        category  = f.get("category", "General")
        weight    = f.get("weight", 1)
        your_raw  = normalise_status(f.get("your_status", "no"))
        your_s    = STATUS_SCORE[your_raw]
        comp_raw  = {c: normalise_status(f.get("competitors", {}).get(c, "no"))
                     for c in competitors}
        comp_s    = {c: STATUS_SCORE[comp_raw[c]] for c in competitors}

        you_win   = all(your_s > comp_s[c] for c in competitors) if competitors else False
        you_lose  = any(your_s < comp_s[c] for c in competitors)
        your_max  = max(comp_s.values()) if comp_s else 0
        advantage = your_s - your_max   # positive = you're better overall

        feature_rows.append({
            "name":          fname,
            "category":      category,
            "weight":        weight,
            "your_status":   your_raw,
            "your_score":    your_s,
            "competitors":   comp_raw,
            "comp_scores":   comp_s,
            "you_win":       you_win,
            "you_lose":      you_lose,
            "advantage":     advantage,
            "notes":         f.get("notes", ""),
        })

    # --- competitive scores per competitor ---
    comp_scores = {}
    for c in competitors:
        wins   = sum(1 for r in feature_rows if r["your_score"] > r["comp_scores"].get(c, 0))
        ties   = sum(1 for r in feature_rows if r["your_score"] == r["comp_scores"].get(c, 0))
        losses = sum(1 for r in feature_rows if r["your_score"] < r["comp_scores"].get(c, 0))
        total  = len(feature_rows)
        score  = round((wins / total) * 100) if total else 0
        comp_scores[c] = {
            "wins": wins, "ties": ties, "losses": losses,
            "win_pct": score,
            "verdict": _verdict(score),
        }

    # Overall competitive score (average win% across all competitors)
    overall_win_pct = (
        round(sum(v["win_pct"] for v in comp_scores.values()) / len(comp_scores))
        if comp_scores else 0
    )

    # Advantages and gaps
    advantages = [r["name"] for r in feature_rows if r["advantage"] > 0]
    gaps       = [r["name"] for r in feature_rows if r["advantage"] < 0]
    parity     = [r["name"] for r in feature_rows if r["advantage"] == 0]

    return {
        "meta": {
            "your_product":     your_product,
            "competitors":      competitors,
            "categories":       categories,
            "total_features":   len(feature_rows),
            "overall_win_pct":  overall_win_pct,
            "verdict":          _verdict(overall_win_pct),
        },
        "competitor_scores": comp_scores,
        "advantages":        advantages,
        "gaps":              gaps,
        "parity":            parity,
        "features":          feature_rows,
    }

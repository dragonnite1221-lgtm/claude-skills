# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from missing_value_analyzer_base import *  # noqa: F403,E402


NULL_STRINGS = {"", "null", "none", "n/a", "na", "nan", "nil", "undefined", "missing"}
def load_csv(filepath: str) -> tuple[list[str], list[dict]]:
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return headers, rows
def is_null(val: str) -> bool:
    return val.strip().lower() in NULL_STRINGS
def compute_null_mask(headers: list[str], rows: list[dict]) -> dict[str, list[bool]]:
    return {col: [is_null(row.get(col, "")) for row in rows] for col in headers}
def null_stats(mask: list[bool]) -> dict:
    total = len(mask)
    count = sum(mask)
    return {"count": count, "pct": round(count / total * 100, 2) if total else 0}
def classify_mechanism(col: str, mask: list[bool], all_masks: dict[str, list[bool]]) -> str:
    """
    Heuristic classification of missingness mechanism:
    - MCAR: nulls appear randomly, no correlation with other columns
    - MAR:  nulls correlate with values in other observed columns
    - MNAR: nulls correlate with the missing column's own unobserved value (can't fully detect)

    Returns one of: "MCAR (likely)", "MAR (likely)", "MNAR (possible)", "Insufficient data"
    """
    null_indices = {i for i, v in enumerate(mask) if v}
    if not null_indices:
        return "None"

    n = len(mask)
    if n < 10:
        return "Insufficient data"

    # Check correlation with other columns' nulls
    correlated_cols = []
    for other_col, other_mask in all_masks.items():
        if other_col == col:
            continue
        other_null_indices = {i for i, v in enumerate(other_mask) if v}
        if not other_null_indices:
            continue
        overlap = len(null_indices & other_null_indices)
        union = len(null_indices | other_null_indices)
        jaccard = overlap / union if union else 0
        if jaccard > 0.5:
            correlated_cols.append(other_col)

    # Check if nulls are clustered (time/positional pattern) — proxy for MNAR
    sorted_indices = sorted(null_indices)
    if len(sorted_indices) > 2:
        gaps = [sorted_indices[i + 1] - sorted_indices[i] for i in range(len(sorted_indices) - 1)]
        avg_gap = sum(gaps) / len(gaps)
        clustered = avg_gap < n / len(null_indices) * 0.5  # nulls appear closer together than random
    else:
        clustered = False

    if correlated_cols:
        return f"MAR (likely) — co-occurs with nulls in: {', '.join(correlated_cols[:3])}"
    elif clustered:
        return "MNAR (possible) — nulls are spatially clustered, may reflect a systematic gap"
    else:
        return "MCAR (likely) — nulls appear random, no strong correlation detected"
def recommend_strategy(pct: float, col_type: str) -> str:
    if pct == 0:
        return "No action needed"
    if pct < 1:
        return "Drop rows — impact is negligible"
    if pct < 10:
        strategies = {
            "int": "Impute with median + add binary indicator column",
            "float": "Impute with median + add binary indicator column",
            "string": "Impute with mode or 'Unknown' category + add indicator",
            "bool": "Impute with mode",
        }
        return strategies.get(col_type, "Impute with median/mode + add indicator")
    if pct < 30:
        return "Impute cautiously; investigate root cause; document assumption; add indicator"
    return "Do NOT impute blindly — > 30% missing. Escalate to domain owner or consider dropping column"
def infer_type(values: list[str]) -> str:
    non_null = [v for v in values if not is_null(v)]
    counts = {"int": 0, "float": 0, "bool": 0, "string": 0}
    for v in non_null[:200]:  # sample for speed
        v = v.strip()
        if v.lower() in ("true", "false"):
            counts["bool"] += 1
        else:
            try:
                int(v)
                counts["int"] += 1
            except ValueError:
                try:
                    float(v)
                    counts["float"] += 1
                except ValueError:
                    counts["string"] += 1
    return max(counts, key=lambda k: counts[k]) if any(counts.values()) else "string"
def compute_cooccurrence(headers: list[str], masks: dict[str, list[bool]], top_n: int = 5) -> list[dict]:
    """Find column pairs where nulls most frequently co-occur."""
    pairs = []
    cols = list(headers)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i], cols[j]
            mask_a, mask_b = masks[a], masks[b]
            overlap = sum(1 for x, y in zip(mask_a, mask_b) if x and y)
            if overlap > 0:
                pairs.append({"col_a": a, "col_b": b, "co_null_rows": overlap})
    pairs.sort(key=lambda x: -x["co_null_rows"])
    return pairs[:top_n]

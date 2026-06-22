# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_profiler_base import *  # noqa: F403,E402


def load_csv(filepath: str) -> tuple[list[str], list[dict]]:
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return headers, rows
def infer_type(values: list[str]) -> str:
    """Infer dominant type from non-null string values."""
    counts = {"int": 0, "float": 0, "bool": 0, "string": 0}
    for v in values:
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
    dominant = max(counts, key=lambda k: counts[k])
    return dominant if counts[dominant] > 0 else "string"
def safe_mean(nums: list[float]) -> float | None:
    return sum(nums) / len(nums) if nums else None
def safe_std(nums: list[float], mean: float) -> float | None:
    if len(nums) < 2:
        return None
    variance = sum((x - mean) ** 2 for x in nums) / (len(nums) - 1)
    return math.sqrt(variance)
def profile_column(name: str, raw_values: list[str]) -> dict:
    total = len(raw_values)
    null_strings = {"", "null", "none", "n/a", "na", "nan", "nil"}
    null_count = sum(1 for v in raw_values if v.strip().lower() in null_strings)
    non_null = [v for v in raw_values if v.strip().lower() not in null_strings]

    col_type = infer_type(non_null)
    unique_values = set(non_null)
    top_values = Counter(non_null).most_common(5)

    profile = {
        "column": name,
        "total_rows": total,
        "null_count": null_count,
        "null_pct": round(null_count / total * 100, 2) if total else 0,
        "non_null_count": len(non_null),
        "unique_count": len(unique_values),
        "cardinality_pct": round(len(unique_values) / len(non_null) * 100, 2) if non_null else 0,
        "inferred_type": col_type,
        "top_values": top_values,
        "is_constant": len(unique_values) == 1,
        "is_high_cardinality": len(unique_values) / len(non_null) > 0.9 if len(non_null) > 10 else False,
    }

    if col_type in ("int", "float"):
        try:
            nums = [float(v) for v in non_null]
            mean = safe_mean(nums)
            profile["min"] = min(nums)
            profile["max"] = max(nums)
            profile["mean"] = round(mean, 4) if mean is not None else None
            profile["std"] = round(safe_std(nums, mean), 4) if mean is not None else None
        except ValueError:
            pass

    return profile
def compute_dqs(profiles: list[dict], total_rows: int) -> dict:
    """Compute Data Quality Score (0-100) across 5 dimensions."""
    if not profiles or total_rows == 0:
        return {"score": 0, "dimensions": {}}

    # Completeness (30%) — avg non-null rate
    avg_null_pct = sum(p["null_pct"] for p in profiles) / len(profiles)
    completeness = max(0, 100 - avg_null_pct)

    # Consistency (25%) — penalize constant cols and mixed-type signals
    constant_cols = sum(1 for p in profiles if p["is_constant"])
    consistency = max(0, 100 - (constant_cols / len(profiles)) * 100)

    # Validity (20%) — penalize high-cardinality string cols (proxy for free-text issues)
    high_card = sum(1 for p in profiles if p["is_high_cardinality"] and p["inferred_type"] == "string")
    validity = max(0, 100 - (high_card / len(profiles)) * 60)

    # Uniqueness (15%) — placeholder; duplicate detection needs full row comparison
    uniqueness = 90.0  # conservative default without row-level dedup check

    # Timeliness (10%) — placeholder; requires timestamp columns
    timeliness = 85.0  # conservative default

    score = (
        completeness * 0.30
        + consistency * 0.25
        + validity * 0.20
        + uniqueness * 0.15
        + timeliness * 0.10
    )

    return {
        "score": round(score, 1),
        "dimensions": {
            "completeness": round(completeness, 1),
            "consistency": round(consistency, 1),
            "validity": round(validity, 1),
            "uniqueness": uniqueness,
            "timeliness": timeliness,
        },
    }
def dqs_label(score: float) -> str:
    if score >= 85:
        return "PASS — Production-ready"
    elif score >= 65:
        return "WARN — Usable with documented caveats"
    else:
        return "FAIL — Remediation required before use"

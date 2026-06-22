# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from outlier_detector_base import *  # noqa: F403,E402


NULL_STRINGS = {"", "null", "none", "n/a", "na", "nan", "nil", "undefined", "missing"}
def load_csv(filepath: str) -> tuple[list[str], list[dict]]:
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return headers, rows
def is_null(val: str) -> bool:
    return val.strip().lower() in NULL_STRINGS
def to_float(val: str) -> float | None:
    try:
        return float(val.strip())
    except (ValueError, AttributeError):
        return None
def median(nums: list[float]) -> float:
    s = sorted(nums)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2
def percentile(nums: list[float], p: float) -> float:
    """Linear interpolation percentile."""
    s = sorted(nums)
    n = len(s)
    if n == 1:
        return s[0]
    idx = p / 100 * (n - 1)
    lo = int(idx)
    hi = lo + 1
    frac = idx - lo
    if hi >= n:
        return s[-1]
    return s[lo] + frac * (s[hi] - s[lo])
def mean(nums: list[float]) -> float:
    return sum(nums) / len(nums)
def std(nums: list[float], mu: float) -> float:
    if len(nums) < 2:
        return 0.0
    variance = sum((x - mu) ** 2 for x in nums) / (len(nums) - 1)
    return math.sqrt(variance)
def detect_iqr(nums: list[float], multiplier: float = 1.5) -> dict:
    q1 = percentile(nums, 25)
    q3 = percentile(nums, 75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    outliers = [x for x in nums if x < lower or x > upper]
    return {
        "method": "IQR",
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lower_bound": round(lower, 4),
        "upper_bound": round(upper, 4),
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(nums) * 100, 2),
        "outlier_values": sorted(set(round(x, 4) for x in outliers))[:10],
    }
def detect_zscore(nums: list[float], threshold: float = 3.0) -> dict:
    mu = mean(nums)
    sigma = std(nums, mu)
    if sigma == 0:
        return {"method": "Z-score", "outlier_count": 0, "outlier_pct": 0.0,
                "note": "Zero variance — all values identical"}
    zscores = [(x, abs((x - mu) / sigma)) for x in nums]
    outliers = [x for x, z in zscores if z > threshold]
    return {
        "method": "Z-score",
        "mean": round(mu, 4),
        "std": round(sigma, 4),
        "threshold": threshold,
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(nums) * 100, 2),
        "outlier_values": sorted(set(round(x, 4) for x in outliers))[:10],
    }
def detect_modified_zscore(nums: list[float], threshold: float = 3.5) -> dict:
    """Iglewicz-Hoaglin modified Z-score using Median Absolute Deviation."""
    med = median(nums)
    mad = median([abs(x - med) for x in nums])
    if mad == 0:
        return {"method": "Modified Z-score (MAD)", "outlier_count": 0, "outlier_pct": 0.0,
                "note": "MAD is zero — consider Z-score instead"}
    mzscores = [(x, 0.6745 * abs(x - med) / mad) for x in nums]
    outliers = [x for x, mz in mzscores if mz > threshold]
    return {
        "method": "Modified Z-score (MAD)",
        "median": round(med, 4),
        "mad": round(mad, 4),
        "threshold": threshold,
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(nums) * 100, 2),
        "outlier_values": sorted(set(round(x, 4) for x in outliers))[:10],
    }
def classify_outlier_risk(pct: float, col: str) -> str:
    """Heuristic: flag whether outliers are likely data errors or legitimate extremes."""
    if pct > 10:
        return "High outlier rate — likely systematic data quality issue or wrong data type"
    if pct > 5:
        return "Elevated outlier rate — investigate source; may be mixed populations"
    if pct > 1:
        return "Moderate — review individually; could be legitimate extremes or entry errors"
    if pct > 0:
        return "Low — verify extreme values against source; likely legitimate but worth checking"
    return "Clean — no outliers detected"
def analyze_column(col: str, nums: list[float], method: str, threshold: float) -> dict:
    if len(nums) < 4:
        return {"column": col, "status": "Skipped — fewer than 4 numeric values"}

    if method == "iqr":
        result = detect_iqr(nums, multiplier=threshold if threshold != 3.0 else 1.5)
    elif method == "zscore":
        result = detect_zscore(nums, threshold=threshold)
    elif method == "mzscore":
        result = detect_modified_zscore(nums, threshold=threshold)
    else:
        result = detect_iqr(nums)

    result["column"] = col
    result["total_numeric"] = len(nums)
    result["risk_assessment"] = classify_outlier_risk(result.get("outlier_pct", 0), col)
    return result

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_score_calculator_base import *  # noqa: F403,E402


DIMENSION_WEIGHTS: Dict[str, float] = {
    "usage": 0.30,
    "engagement": 0.25,
    "support": 0.20,
    "relationship": 0.25,
}
SEGMENT_THRESHOLDS: Dict[str, Dict[str, Tuple[int, int]]] = {
    "enterprise": {"green": (75, 100), "yellow": (50, 74), "red": (0, 49)},
    "mid-market": {"green": (70, 100), "yellow": (45, 69), "red": (0, 44)},
    "smb": {"green": (65, 100), "yellow": (40, 64), "red": (0, 39)},
}
SEGMENT_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "enterprise": {
        "login_frequency_target": 90,
        "feature_adoption_target": 80,
        "dau_mau_target": 0.50,
        "support_ticket_volume_max": 5,
        "meeting_attendance_target": 95,
        "nps_target": 9,
        "csat_target": 4.5,
        "open_tickets_max": 10,
        "escalation_rate_max": 0.25,
        "avg_resolution_hours_max": 72,
        "exec_sponsor_target": 90,
        "multi_threading_target": 5,
    },
    "mid-market": {
        "login_frequency_target": 80,
        "feature_adoption_target": 70,
        "dau_mau_target": 0.40,
        "support_ticket_volume_max": 8,
        "meeting_attendance_target": 85,
        "nps_target": 8,
        "csat_target": 4.0,
        "open_tickets_max": 15,
        "escalation_rate_max": 0.30,
        "avg_resolution_hours_max": 96,
        "exec_sponsor_target": 75,
        "multi_threading_target": 3,
    },
    "smb": {
        "login_frequency_target": 70,
        "feature_adoption_target": 60,
        "dau_mau_target": 0.30,
        "support_ticket_volume_max": 10,
        "meeting_attendance_target": 75,
        "nps_target": 7,
        "csat_target": 3.8,
        "open_tickets_max": 20,
        "escalation_rate_max": 0.40,
        "avg_resolution_hours_max": 120,
        "exec_sponsor_target": 60,
        "multi_threading_target": 2,
    },
}
RENEWAL_SENTIMENT_SCORES: Dict[str, float] = {
    "positive": 100.0,
    "neutral": 60.0,
    "negative": 20.0,
    "unknown": 50.0,
}
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Return numerator / denominator, or *default* when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp *value* between *lo* and *hi*."""
    return max(lo, min(hi, value))
def get_benchmarks(segment: str) -> Dict[str, Any]:
    """Return benchmarks for the given segment, falling back to mid-market."""
    return SEGMENT_BENCHMARKS.get(segment.lower(), SEGMENT_BENCHMARKS["mid-market"])
def get_thresholds(segment: str) -> Dict[str, Tuple[int, int]]:
    """Return classification thresholds for the given segment."""
    return SEGMENT_THRESHOLDS.get(segment.lower(), SEGMENT_THRESHOLDS["mid-market"])
def classify(score: float, segment: str) -> str:
    """Return 'green', 'yellow', or 'red' classification."""
    thresholds = get_thresholds(segment)
    if score >= thresholds["green"][0]:
        return "green"
    elif score >= thresholds["yellow"][0]:
        return "yellow"
    return "red"
def trend_direction(current: float, previous: Optional[float]) -> str:
    """Return trend direction string."""
    if previous is None:
        return "no_data"
    diff = current - previous
    if diff > 5:
        return "improving"
    elif diff < -5:
        return "declining"
    return "stable"
def score_usage(data: Dict[str, Any], benchmarks: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score the usage dimension (0-100).

    Metrics: login_frequency, feature_adoption, dau_mau_ratio.
    """
    recommendations: List[str] = []

    login = clamp(safe_divide(data.get("login_frequency", 0), benchmarks["login_frequency_target"]) * 100)
    adoption = clamp(safe_divide(data.get("feature_adoption", 0), benchmarks["feature_adoption_target"]) * 100)
    dau_mau = clamp(safe_divide(data.get("dau_mau_ratio", 0), benchmarks["dau_mau_target"]) * 100)

    score = round(login * 0.35 + adoption * 0.40 + dau_mau * 0.25, 1)

    if login < 60:
        recommendations.append("Login frequency below target -- schedule product engagement session")
    if adoption < 50:
        recommendations.append("Feature adoption is low -- recommend guided feature walkthrough")
    if dau_mau < 50:
        recommendations.append("DAU/MAU ratio indicates shallow usage -- investigate stickiness barriers")

    return score, recommendations

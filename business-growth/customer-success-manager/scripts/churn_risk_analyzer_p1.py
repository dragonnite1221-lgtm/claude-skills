# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_risk_analyzer_base import *  # noqa: F403,E402


RISK_SIGNAL_WEIGHTS: Dict[str, float] = {
    "usage_decline": 0.30,
    "engagement_drop": 0.25,
    "support_issues": 0.20,
    "relationship_signals": 0.15,
    "commercial_factors": 0.10,
}
RISK_TIERS: List[Dict[str, Any]] = [
    {"name": "critical", "min": 80, "max": 100, "label": "CRITICAL", "action": "Immediate executive escalation"},
    {"name": "high", "min": 60, "max": 79, "label": "HIGH", "action": "Urgent CSM intervention"},
    {"name": "medium", "min": 40, "max": 59, "label": "MEDIUM", "action": "Proactive outreach"},
    {"name": "low", "min": 0, "max": 39, "label": "LOW", "action": "Standard monitoring"},
]
WARNING_SEVERITY: Dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}
INTERVENTION_PLAYBOOKS: Dict[str, List[str]] = {
    "critical": [
        "Schedule executive-to-executive call within 48 hours",
        "Create detailed save plan with specific value milestones",
        "Offer concessions or contract restructuring if needed",
        "Assign dedicated rescue team (CSM + Solutions Engineer)",
        "Daily internal stand-up on account status until stabilised",
        "Prepare competitive displacement defence strategy",
    ],
    "high": [
        "Schedule urgent CSM call within 1 week",
        "Conduct root cause analysis on declining metrics",
        "Build 30-day recovery plan with measurable checkpoints",
        "Re-engage executive sponsor for alignment meeting",
        "Accelerate any pending feature requests or bug fixes",
        "Increase touch frequency to weekly until improvement",
    ],
    "medium": [
        "Schedule proactive check-in within 2 weeks",
        "Share relevant success stories and best practices",
        "Propose training session or product walkthrough",
        "Review current usage against success plan goals",
        "Identify and address any unvoiced concerns",
        "Bi-weekly monitoring until score improves to Low",
    ],
    "low": [
        "Maintain standard touch cadence",
        "Share product updates and new feature announcements",
        "Monitor health score trends monthly",
        "Proactively share relevant industry insights",
        "Prepare for upcoming renewal conversations (if within 90 days)",
    ],
}
SATISFACTION_TREND_SCORES: Dict[str, float] = {
    "improving": 10.0,
    "stable": 30.0,
    "declining": 70.0,
    "critical": 95.0,
}
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Return numerator / denominator, or *default* when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp *value* between *lo* and *hi*."""
    return max(lo, min(hi, value))
def days_until(date_str: Optional[str]) -> Optional[int]:
    """Return days from today until *date_str* (ISO format), or None."""
    if not date_str:
        return None
    try:
        target = datetime.strptime(date_str[:10], "%Y-%m-%d")
        delta = (target - datetime.now()).days
        return max(delta, 0)
    except (ValueError, TypeError):
        return None
def renewal_urgency_multiplier(days_remaining: Optional[int]) -> float:
    """Return a multiplier (1.0 - 1.5) based on proximity to renewal.

    Closer renewals amplify the risk score.
    """
    if days_remaining is None:
        return 1.0
    if days_remaining <= 30:
        return 1.5
    elif days_remaining <= 60:
        return 1.35
    elif days_remaining <= 90:
        return 1.2
    elif days_remaining <= 180:
        return 1.1
    return 1.0
def get_risk_tier(score: float) -> Dict[str, Any]:
    """Return the risk tier dict matching the score."""
    for tier in RISK_TIERS:
        if tier["min"] <= score <= tier["max"]:
            return tier
    return RISK_TIERS[-1]  # default to low
def score_usage_decline(data: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
    """Score usage decline signals (0-100, higher = more risk)."""
    warnings: List[Dict[str, str]] = []

    login_trend = data.get("login_trend", 0)  # negative = decline
    feature_change = data.get("feature_adoption_change", 0)
    dau_mau_change = data.get("dau_mau_change", 0)

    # Convert declines to risk scores (0-100)
    login_risk = clamp(abs(min(login_trend, 0)) * 3.0)  # -33% => 100
    feature_risk = clamp(abs(min(feature_change, 0)) * 4.0)  # -25% => 100
    dau_mau_risk = clamp(abs(min(dau_mau_change, 0)) * 500)  # -0.20 => 100

    score = round(login_risk * 0.40 + feature_risk * 0.35 + dau_mau_risk * 0.25, 1)

    if login_trend <= -20:
        warnings.append({"severity": "critical", "signal": f"Login frequency dropped {abs(login_trend)}%"})
    elif login_trend <= -10:
        warnings.append({"severity": "high", "signal": f"Login frequency declined {abs(login_trend)}%"})
    elif login_trend < -5:
        warnings.append({"severity": "medium", "signal": f"Login frequency dipping {abs(login_trend)}%"})

    if feature_change <= -15:
        warnings.append({"severity": "high", "signal": f"Feature adoption dropped {abs(feature_change)}%"})
    elif feature_change < -5:
        warnings.append({"severity": "medium", "signal": f"Feature adoption declining {abs(feature_change)}%"})

    if dau_mau_change <= -0.10:
        warnings.append({"severity": "high", "signal": f"DAU/MAU ratio fell by {abs(dau_mau_change):.2f}"})

    return score, warnings

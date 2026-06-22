# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_risk_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_risk_analyzer_p1 import SATISFACTION_TREND_SCORES, clamp  # noqa: E402,E501
# fmt: on


def score_engagement_drop(data: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
    """Score engagement drop signals (0-100, higher = more risk)."""
    warnings: List[Dict[str, str]] = []

    cancellations = data.get("meeting_cancellations", 0)
    response_days = data.get("response_time_days", 1)
    nps_change = data.get("nps_change", 0)

    cancel_risk = clamp(cancellations * 25.0)  # 4 cancellations => 100
    response_risk = clamp((response_days - 1) * 15.0)  # 1 day baseline; 7+ days => 90+
    nps_risk = clamp(abs(min(nps_change, 0)) * 20.0)  # -5 => 100

    score = round(cancel_risk * 0.30 + response_risk * 0.35 + nps_risk * 0.35, 1)

    if cancellations >= 3:
        warnings.append({"severity": "critical", "signal": f"{cancellations} meeting cancellations -- customer disengaging"})
    elif cancellations >= 2:
        warnings.append({"severity": "high", "signal": f"{cancellations} meeting cancellations recently"})

    if response_days >= 7:
        warnings.append({"severity": "critical", "signal": f"Customer response time: {response_days} days -- going dark"})
    elif response_days >= 4:
        warnings.append({"severity": "high", "signal": f"Customer response time increasing: {response_days} days"})

    if nps_change <= -4:
        warnings.append({"severity": "critical", "signal": f"NPS dropped by {abs(nps_change)} points"})
    elif nps_change <= -2:
        warnings.append({"severity": "high", "signal": f"NPS declined by {abs(nps_change)} points"})

    return score, warnings
def score_support_issues(data: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
    """Score support-related risk signals (0-100, higher = more risk)."""
    warnings: List[Dict[str, str]] = []

    escalations = data.get("open_escalations", 0)
    critical_unresolved = data.get("unresolved_critical", 0)
    sat_trend = data.get("satisfaction_trend", "stable").lower()

    esc_risk = clamp(escalations * 35.0)  # 3 escalations => 100
    critical_risk = clamp(critical_unresolved * 50.0)  # 2 unresolved critical => 100
    sat_risk = SATISFACTION_TREND_SCORES.get(sat_trend, 30.0)

    score = round(esc_risk * 0.35 + critical_risk * 0.35 + sat_risk * 0.30, 1)

    if critical_unresolved >= 2:
        warnings.append({"severity": "critical", "signal": f"{critical_unresolved} unresolved critical support tickets"})
    elif critical_unresolved >= 1:
        warnings.append({"severity": "high", "signal": "Unresolved critical support ticket"})

    if escalations >= 2:
        warnings.append({"severity": "high", "signal": f"{escalations} open escalations"})
    elif escalations >= 1:
        warnings.append({"severity": "medium", "signal": "Open support escalation"})

    if sat_trend == "critical":
        warnings.append({"severity": "critical", "signal": "Support satisfaction at critical levels"})
    elif sat_trend == "declining":
        warnings.append({"severity": "high", "signal": "Support satisfaction trending down"})

    return score, warnings
def score_relationship_signals(data: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
    """Score relationship risk signals (0-100, higher = more risk)."""
    warnings: List[Dict[str, str]] = []
    risk_points = 0.0

    champion_left = data.get("champion_left", False)
    sponsor_change = data.get("sponsor_change", False)
    competitor_mentions = data.get("competitor_mentions", 0)

    if champion_left:
        risk_points += 45.0
        warnings.append({"severity": "critical", "signal": "Internal champion has left the organisation"})

    if sponsor_change:
        risk_points += 30.0
        warnings.append({"severity": "high", "signal": "Executive sponsor change detected"})

    if competitor_mentions >= 3:
        risk_points += 35.0
        warnings.append({"severity": "critical", "signal": f"Customer mentioned competitors {competitor_mentions} times"})
    elif competitor_mentions >= 1:
        risk_points += competitor_mentions * 12.0
        warnings.append({"severity": "medium", "signal": f"Customer mentioned competitor {competitor_mentions} time(s)"})

    score = clamp(risk_points)
    return round(score, 1), warnings
def score_commercial_factors(data: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
    """Score commercial risk factors (0-100, higher = more risk)."""
    warnings: List[Dict[str, str]] = []
    risk_points = 0.0

    contract_type = data.get("contract_type", "annual").lower()
    pricing_complaints = data.get("pricing_complaints", False)
    budget_cuts = data.get("budget_cuts_mentioned", False)

    if contract_type == "month-to-month":
        risk_points += 30.0
        warnings.append({"severity": "medium", "signal": "Month-to-month contract -- low switching cost"})
    elif contract_type == "quarterly":
        risk_points += 15.0

    if pricing_complaints:
        risk_points += 35.0
        warnings.append({"severity": "high", "signal": "Customer has raised pricing complaints"})

    if budget_cuts:
        risk_points += 40.0
        warnings.append({"severity": "high", "signal": "Customer mentioned budget cuts or cost reduction"})

    score = clamp(risk_points)
    return round(score, 1), warnings

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_score_calculator_base import *  # noqa: F403,E402
# fmt: off
from health_score_calculator_p1 import RENEWAL_SENTIMENT_SCORES, clamp, safe_divide  # noqa: E402,E501
# fmt: on


def score_engagement(data: Dict[str, Any], benchmarks: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score the engagement dimension (0-100).

    Metrics: support_ticket_volume (inverse), meeting_attendance, nps_score, csat_score.
    """
    recommendations: List[str] = []

    # Lower ticket volume is better -- invert
    ticket_vol = data.get("support_ticket_volume", 0)
    ticket_score = clamp((1.0 - safe_divide(ticket_vol, benchmarks["support_ticket_volume_max"])) * 100)

    attendance = clamp(safe_divide(data.get("meeting_attendance", 0), benchmarks["meeting_attendance_target"]) * 100)

    nps_raw = data.get("nps_score", 5)
    nps_score = clamp(safe_divide(nps_raw, benchmarks["nps_target"]) * 100)

    csat_raw = data.get("csat_score", 3.0)
    csat_score = clamp(safe_divide(csat_raw, benchmarks["csat_target"]) * 100)

    score = round(ticket_score * 0.20 + attendance * 0.30 + nps_score * 0.25 + csat_score * 0.25, 1)

    if attendance < 60:
        recommendations.append("Meeting attendance is low -- re-evaluate meeting cadence and agenda value")
    if nps_raw < 7:
        recommendations.append("NPS below threshold -- conduct a feedback deep-dive with customer")
    if csat_raw < 3.5:
        recommendations.append("CSAT is critically low -- escalate to support leadership")

    return score, recommendations
def score_support(data: Dict[str, Any], benchmarks: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score the support dimension (0-100).

    Metrics: open_tickets (inverse), escalation_rate (inverse), avg_resolution_hours (inverse).
    """
    recommendations: List[str] = []

    open_tix = data.get("open_tickets", 0)
    open_score = clamp((1.0 - safe_divide(open_tix, benchmarks["open_tickets_max"])) * 100)

    esc_rate = data.get("escalation_rate", 0)
    esc_score = clamp((1.0 - safe_divide(esc_rate, benchmarks["escalation_rate_max"])) * 100)

    res_hours = data.get("avg_resolution_hours", 0)
    res_score = clamp((1.0 - safe_divide(res_hours, benchmarks["avg_resolution_hours_max"])) * 100)

    score = round(open_score * 0.35 + esc_score * 0.35 + res_score * 0.30, 1)

    if open_tix > benchmarks["open_tickets_max"] * 0.5:
        recommendations.append("Open ticket count elevated -- prioritise ticket resolution")
    if esc_rate > benchmarks["escalation_rate_max"] * 0.5:
        recommendations.append("Escalation rate too high -- review support process and training")
    if res_hours > benchmarks["avg_resolution_hours_max"] * 0.5:
        recommendations.append("Resolution time exceeds SLA target -- engage support leadership")

    return score, recommendations
def score_relationship(data: Dict[str, Any], benchmarks: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score the relationship dimension (0-100).

    Metrics: executive_sponsor_engagement, multi_threading_depth, renewal_sentiment.
    """
    recommendations: List[str] = []

    exec_score = clamp(safe_divide(data.get("executive_sponsor_engagement", 0), benchmarks["exec_sponsor_target"]) * 100)

    threading = data.get("multi_threading_depth", 1)
    thread_score = clamp(safe_divide(threading, benchmarks["multi_threading_target"]) * 100)

    sentiment_str = data.get("renewal_sentiment", "unknown").lower()
    sentiment_score = RENEWAL_SENTIMENT_SCORES.get(sentiment_str, 50.0)

    score = round(exec_score * 0.35 + thread_score * 0.30 + sentiment_score * 0.35, 1)

    if exec_score < 50:
        recommendations.append("Executive sponsor engagement is weak -- schedule executive alignment meeting")
    if threading < 2:
        recommendations.append("Single-threaded relationship -- expand contacts across departments")
    if sentiment_str == "negative":
        recommendations.append("Renewal sentiment is negative -- initiate save plan immediately")

    return score, recommendations

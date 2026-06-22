# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import DIMENSION_WEIGHTS, ERROR_RATE_THRESHOLDS, LATENCY_P99_THRESHOLDS_MS, SeverityLevel  # noqa: E402,E501
from severity_classifier_p2 import ImpactAssessment, SeverityScore  # noqa: E402,E501
from severity_classifier_p3 import _score_data_security, _score_revenue_impact, _score_service_criticality, _score_user_impact  # noqa: E402,E501
# fmt: on


def _score_blast_radius(
    impact: ImpactAssessment, signals: Dict
) -> Tuple[float, List[str]]:
    """Score blast radius from region spread, alert volume, and error rate."""
    factors: List[str] = []
    score = 0.0

    region_count = len(impact.affected_regions)
    if region_count >= 3:
        score = 0.9
        factors.append(f"Spanning {region_count} regions")
    elif region_count == 2:
        score = 0.6
        factors.append(f"Spanning {region_count} regions")
    elif region_count == 1:
        score = 0.3

    error_rate = signals.get("error_rate_percentage", 0.0)
    for threshold, rate_score in ERROR_RATE_THRESHOLDS:
        if error_rate >= threshold:
            score = max(score, rate_score)
            factors.append(f"Error rate at {error_rate}%")
            break

    latency = signals.get("latency_p99_ms", 0)
    for threshold, lat_score in LATENCY_P99_THRESHOLDS_MS:
        if latency >= threshold:
            score = max(score, lat_score)
            factors.append(f"P99 latency at {latency}ms")
            break

    alert_count = signals.get("alert_count", 0)
    if alert_count >= 20:
        score = min(1.0, score + 0.15)
        factors.append(f"{alert_count} alerts firing")
    elif alert_count >= 10:
        score = min(1.0, score + 0.08)
        factors.append(f"{alert_count} alerts firing")

    return score, factors
def compute_dimension_scores(
    impact: ImpactAssessment, signals: Dict, context: Dict
) -> SeverityScore:
    """Score each weighted dimension and produce a composite severity score."""
    dimensions: Dict[str, float] = {}
    weighted: Dict[str, float] = {}
    all_factors: List[str] = []
    auto_escalate: List[str] = []

    # -- Revenue impact --
    rev_score, rev_factors = _score_revenue_impact(impact)
    dimensions["revenue_impact"] = round(rev_score, 3)
    weighted["revenue_impact"] = round(rev_score * DIMENSION_WEIGHTS["revenue_impact"], 3)
    all_factors.extend(rev_factors)

    # -- User impact scope --
    user_score, user_factors = _score_user_impact(impact, signals)
    dimensions["user_impact_scope"] = round(user_score, 3)
    weighted["user_impact_scope"] = round(user_score * DIMENSION_WEIGHTS["user_impact_scope"], 3)
    all_factors.extend(user_factors)

    # -- Data / security risk --
    sec_score, sec_factors = _score_data_security(impact)
    dimensions["data_security_risk"] = round(sec_score, 3)
    weighted["data_security_risk"] = round(sec_score * DIMENSION_WEIGHTS["data_security_risk"], 3)
    all_factors.extend(sec_factors)

    # -- Service criticality --
    svc_score, svc_factors = _score_service_criticality(signals, context)
    dimensions["service_criticality"] = round(svc_score, 3)
    weighted["service_criticality"] = round(svc_score * DIMENSION_WEIGHTS["service_criticality"], 3)
    all_factors.extend(svc_factors)

    # -- Blast radius --
    blast_score, blast_factors = _score_blast_radius(impact, signals)
    dimensions["blast_radius"] = round(blast_score, 3)
    weighted["blast_radius"] = round(blast_score * DIMENSION_WEIGHTS["blast_radius"], 3)
    all_factors.extend(blast_factors)

    composite = sum(weighted.values())

    # -- Auto-escalation overrides --
    if impact.security_breach:
        composite = max(composite, 0.85)
        auto_escalate.append("Security breach triggers automatic SEV1 escalation")
    if impact.data_integrity_risk and impact.customer_facing:
        composite = max(composite, 0.76)
        auto_escalate.append("Customer-facing data integrity risk triggers SEV1 floor")
    if impact.affected_users_percentage >= 50 and impact.degradation_type == "complete":
        composite = max(composite, 0.80)
        auto_escalate.append("Complete outage affecting 50%+ users triggers SEV1 floor")

    composite = min(1.0, round(composite, 3))
    severity_level = SeverityLevel.from_score(composite)

    return SeverityScore(
        composite_score=composite,
        severity_level=severity_level,
        dimensions=dimensions,
        weighted_dimensions=weighted,
        contributing_factors=all_factors,
        auto_escalate_reasons=auto_escalate,
    )
def classify_severity(
    incident: Dict, impact: ImpactAssessment, signals: Dict, context: Dict
) -> SeverityScore:
    """
    Top-level classification: compute scores and return the final
    SeverityScore including the resolved severity level.
    """
    return compute_dimension_scores(impact, signals, context)

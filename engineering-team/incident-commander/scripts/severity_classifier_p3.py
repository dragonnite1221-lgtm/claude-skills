# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import DEGRADATION_SCORES, REVENUE_IMPACT_SCORES  # noqa: E402,E501
from severity_classifier_p2 import ImpactAssessment  # noqa: E402,E501
# fmt: on


def parse_incident_data(raw: Dict[str, Any]) -> Tuple[Dict, ImpactAssessment, Dict, Dict]:
    """
    Validate and normalise raw JSON input into typed structures.

    Returns:
        (incident_info, impact_assessment, signals, context)
    """
    incident = raw.get("incident", {})
    if not incident:
        raise ValueError("Input must contain an 'incident' key with title and description.")

    impact_raw = raw.get("impact", {})
    impact = ImpactAssessment(
        revenue_impact=impact_raw.get("revenue_impact", "none"),
        affected_users_percentage=float(impact_raw.get("affected_users_percentage", 0)),
        affected_regions=impact_raw.get("affected_regions", []),
        data_integrity_risk=bool(impact_raw.get("data_integrity_risk", False)),
        security_breach=bool(impact_raw.get("security_breach", False)),
        customer_facing=bool(impact_raw.get("customer_facing", False)),
        degradation_type=impact_raw.get("degradation_type", "none"),
        workaround_available=bool(impact_raw.get("workaround_available", True)),
    )

    signals = raw.get("signals", {})
    context = raw.get("context", {})

    return incident, impact, signals, context
def _score_revenue_impact(impact: ImpactAssessment) -> Tuple[float, List[str]]:
    """Score the revenue impact dimension (0.0 - 1.0)."""
    factors: List[str] = []
    score = REVENUE_IMPACT_SCORES.get(impact.revenue_impact, 0.0)

    if impact.customer_facing and score >= 0.5:
        score = min(1.0, score + 0.1)
        factors.append("Customer-facing service with revenue exposure")

    if not impact.workaround_available and score >= 0.5:
        score = min(1.0, score + 0.1)
        factors.append("No workaround available, prolonging revenue impact")

    if score >= 0.8:
        factors.append(f"Revenue impact rated '{impact.revenue_impact}'")

    return score, factors
def _score_user_impact(impact: ImpactAssessment, signals: Dict) -> Tuple[float, List[str]]:
    """Score the user impact scope dimension (0.0 - 1.0)."""
    factors: List[str] = []
    pct = impact.affected_users_percentage

    if pct >= 75:
        score = 1.0
    elif pct >= 50:
        score = 0.85
    elif pct >= 25:
        score = 0.65
    elif pct >= 10:
        score = 0.45
    elif pct >= 1:
        score = 0.25
    else:
        score = 0.1

    if pct > 0:
        factors.append(f"{pct}% of users affected")

    customer_reports = signals.get("customer_reports", 0)
    if customer_reports > 20:
        score = min(1.0, score + 0.15)
        factors.append(f"{customer_reports} customer reports received")
    elif customer_reports > 5:
        score = min(1.0, score + 0.08)
        factors.append(f"{customer_reports} customer reports received")

    degradation_boost = DEGRADATION_SCORES.get(impact.degradation_type, 0.0) * 0.15
    score = min(1.0, score + degradation_boost)
    if impact.degradation_type in ("complete", "major"):
        factors.append(f"Degradation type: {impact.degradation_type}")

    return score, factors
def _score_data_security(impact: ImpactAssessment) -> Tuple[float, List[str]]:
    """Score the data/security risk dimension (0.0 - 1.0)."""
    factors: List[str] = []
    score = 0.0

    if impact.security_breach:
        score = 1.0
        factors.append("Active security breach confirmed")
    elif impact.data_integrity_risk:
        score = 0.8
        factors.append("Data integrity at risk")

    if impact.customer_facing and impact.data_integrity_risk:
        score = min(1.0, score + 0.1)
        factors.append("Customer data potentially affected")

    return score, factors
def _score_service_criticality(signals: Dict, context: Dict) -> Tuple[float, List[str]]:
    """Score service criticality based on signals and dependency graph."""
    factors: List[str] = []
    score = 0.0

    dependent_services = signals.get("dependent_services", [])
    dep_count = len(dependent_services)
    if dep_count >= 5:
        score = 1.0
        factors.append(f"{dep_count} dependent services (critical hub)")
    elif dep_count >= 3:
        score = 0.75
        factors.append(f"{dep_count} dependent services")
    elif dep_count >= 1:
        score = 0.5
        factors.append(f"{dep_count} dependent service(s)")
    else:
        score = 0.2

    affected_endpoints = signals.get("affected_endpoints", [])
    if len(affected_endpoints) >= 5:
        score = min(1.0, score + 0.15)
        factors.append(f"{len(affected_endpoints)} endpoints affected")
    elif len(affected_endpoints) >= 2:
        score = min(1.0, score + 0.08)
        factors.append(f"{len(affected_endpoints)} endpoints affected")

    return score, factors

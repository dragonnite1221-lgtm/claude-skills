# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import DEGRADATION_SCORES  # noqa: E402,E501
from severity_classifier_p2 import ImpactAssessment, SLAImpact, SLA_TIERS, SeverityScore  # noqa: E402,E501
# fmt: on


def assess_sla_impact(
    severity_score: SeverityScore,
    impact: ImpactAssessment,
    signals: Dict,
) -> SLAImpact:
    """Calculate SLA breach risk and error-budget consumption."""
    level = severity_score.severity_level
    tier = SLA_TIERS.get(level, SLA_TIERS["SEV4"])

    # Estimate ongoing burn rate (minutes of budget consumed per real minute)
    user_pct = impact.affected_users_percentage / 100.0
    degradation_factor = DEGRADATION_SCORES.get(impact.degradation_type, 0.25)
    burn_rate = user_pct * degradation_factor
    if burn_rate <= 0:
        burn_rate = 0.01  # minimum if incident is open

    monthly_budget = tier["monthly_error_budget_minutes"]

    # Assume 30% of budget already consumed this month for conservative estimate
    assumed_consumed_pct = 30.0
    remaining_budget = monthly_budget * (1 - assumed_consumed_pct / 100.0)

    if burn_rate > 0:
        time_to_breach = remaining_budget / burn_rate
    else:
        time_to_breach = float("inf")

    # Classify breach risk
    if time_to_breach <= 30:
        breach_risk = "critical"
    elif time_to_breach <= 120:
        breach_risk = "high"
    elif time_to_breach <= 480:
        breach_risk = "medium"
    else:
        breach_risk = "low"

    budget_impact_per_hour = burn_rate * 60
    error_budget_impact = round(budget_impact_per_hour, 2)

    remaining_pct = round(
        max(0.0, (remaining_budget / monthly_budget) * 100.0), 1
    )

    recommendations: List[str] = []
    if breach_risk == "critical":
        recommendations.append(
            "SLA breach imminent. Prioritize resolution above all other work."
        )
        recommendations.append(
            "Prepare customer communication about potential SLA credit."
        )
    elif breach_risk == "high":
        recommendations.append(
            "SLA breach likely within hours. Escalate to ensure rapid resolution."
        )
    elif breach_risk == "medium":
        recommendations.append(
            "Monitor error budget consumption. Resolve before end of business."
        )
    else:
        recommendations.append(
            "SLA impact is contained. Continue standard incident response."
        )

    recommendations.append(
        f"Current burn rate: {round(burn_rate * 100, 1)}% of error budget per minute"
    )
    recommendations.append(
        f"Estimated time to SLA breach: {round(time_to_breach, 0)} minutes "
        f"({round(time_to_breach / 60, 1)} hours)"
    )

    return SLAImpact(
        severity_level=level,
        sla_tier=tier,
        breach_risk=breach_risk,
        error_budget_impact_minutes=error_budget_impact,
        remaining_budget_percentage=remaining_pct,
        estimated_time_to_breach_minutes=round(time_to_breach, 1),
        recommendations=recommendations,
    )
def _header_line(char: str, width: int = 72) -> str:
    return char * width

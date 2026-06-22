# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pipeline_analyzer_p1 import get_quarter, parse_date, safe_divide  # noqa: E402,E501
# fmt: on


def assess_pipeline_risk(
    deals: list[dict], quota: float, stages: list[str]
) -> dict[str, Any]:
    """Assess overall pipeline risk.

    Checks for:
    - Concentration risk (>40% in single deal)
    - Stage distribution health
    - Coverage gap by quarter
    """
    open_deals = [d for d in deals if d["stage"] != "Closed Won"]
    total_pipeline = sum(d["value"] for d in open_deals)

    # Concentration risk
    concentration_risks = []
    for deal in open_deals:
        pct = safe_divide(deal["value"], total_pipeline) * 100
        if pct > 40:
            concentration_risks.append({
                "id": deal["id"],
                "name": deal["name"],
                "value": deal["value"],
                "pct_of_pipeline": round(pct, 1),
                "risk_level": "HIGH",
            })
        elif pct > 25:
            concentration_risks.append({
                "id": deal["id"],
                "name": deal["name"],
                "value": deal["value"],
                "pct_of_pipeline": round(pct, 1),
                "risk_level": "MEDIUM",
            })

    has_concentration_risk = any(
        r["risk_level"] == "HIGH" for r in concentration_risks
    )

    # Stage distribution
    stage_distribution: dict[str, dict] = {}
    for stage in stages:
        if stage == "Closed Won":
            continue
        stage_deals = [d for d in open_deals if d["stage"] == stage]
        count = len(stage_deals)
        value = sum(d["value"] for d in stage_deals)
        stage_distribution[stage] = {
            "count": count,
            "value": value,
            "pct_of_pipeline": round(safe_divide(value, total_pipeline) * 100, 1),
        }

    # Check for empty stages (unhealthy funnel)
    empty_stages = [
        stage for stage, data in stage_distribution.items() if data["count"] == 0
    ]

    # Coverage gap by quarter
    today = date.today()
    quarterly_coverage: dict[str, float] = {}
    for deal in open_deals:
        try:
            close_date = parse_date(deal["close_date"])
            quarter = get_quarter(close_date)
            quarterly_coverage[quarter] = (
                quarterly_coverage.get(quarter, 0) + deal["value"]
            )
        except (ValueError, KeyError):
            pass

    quarterly_target = quota / 4
    coverage_gaps = []
    for quarter, value in sorted(quarterly_coverage.items()):
        coverage = safe_divide(value, quarterly_target)
        if coverage < 3.0:
            coverage_gaps.append({
                "quarter": quarter,
                "pipeline_value": value,
                "quarterly_target": quarterly_target,
                "coverage_ratio": round(coverage, 2),
                "gap": "Below 3x target",
            })

    # Overall risk rating
    risk_factors = 0
    if has_concentration_risk:
        risk_factors += 2
    if len(empty_stages) > 0:
        risk_factors += 1
    if len(coverage_gaps) > 0:
        risk_factors += 1
    if safe_divide(total_pipeline, quota) < 3.0:
        risk_factors += 2

    if risk_factors >= 4:
        overall_risk = "HIGH"
    elif risk_factors >= 2:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "overall_risk": overall_risk,
        "risk_factors_count": risk_factors,
        "concentration_risks": concentration_risks,
        "has_concentration_risk": has_concentration_risk,
        "stage_distribution": stage_distribution,
        "empty_stages": empty_stages,
        "coverage_gaps": coverage_gaps,
    }

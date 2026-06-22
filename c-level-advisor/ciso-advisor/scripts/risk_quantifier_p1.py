# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402


RISK_CATEGORIES = [
    "Data Breach",
    "Ransomware / Extortion",
    "Insider Threat",
    "Third-Party / Supply Chain",
    "Application Vulnerability",
    "Cloud Misconfiguration",
    "Social Engineering",
    "Physical Security",
    "Business Email Compromise",
    "DDoS / Availability",
]
BUSINESS_IMPACT_TYPES = [
    "Revenue Loss",
    "Regulatory Fine",
    "Legal / Litigation",
    "Reputational Damage",
    "Recovery / Remediation Cost",
    "Customer Churn",
    "Business Interruption",
]
MITIGATION_STATUSES = ["None", "Planned", "In Progress", "Mitigated", "Accepted"]
def build_risk(
    name: str,
    category: str,
    description: str,
    asset_value: float,
    exposure_factor: float,  # 0.0–1.0: fraction of asset value lost in breach
    annual_rate: float,      # ARO: expected incidents per year (0.01 = once per 100 years)
    mitigation_cost: float,
    mitigation_effectiveness: float,  # 0.0–1.0: fraction of risk reduced by control
    mitigation_status: str,
    business_impacts: dict,  # {impact_type: dollar_amount}
    notes: str = "",
) -> dict:
    """Construct a risk record with calculated metrics."""
    sle = asset_value * exposure_factor  # Single Loss Expectancy
    ale = sle * annual_rate             # Annual Loss Expectancy (inherent)
    mitigated_ale = ale * (1 - mitigation_effectiveness)  # Residual after mitigation
    mitigation_roi = ((ale - mitigated_ale - mitigation_cost) / mitigation_cost * 100
                      if mitigation_cost > 0 else 0)
    total_business_impact = sum(business_impacts.values())

    return {
        "name": name,
        "category": category,
        "description": description,
        "asset_value": asset_value,
        "exposure_factor": exposure_factor,
        "annual_rate": annual_rate,
        "mitigation_cost": mitigation_cost,
        "mitigation_effectiveness": mitigation_effectiveness,
        "mitigation_status": mitigation_status,
        "business_impacts": business_impacts,
        "notes": notes,
        # Calculated
        "sle": sle,
        "ale": ale,
        "mitigated_ale": mitigated_ale,
        "mitigation_roi_pct": mitigation_roi,
        "total_business_impact": total_business_impact,
        "priority_score": ale,  # Primary sort key
    }

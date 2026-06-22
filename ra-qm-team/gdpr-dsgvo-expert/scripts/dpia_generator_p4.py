# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dpia_generator_base import *  # noqa: F403,E402
# fmt: off
from dpia_generator_p1 import DPIA_TRIGGERS  # noqa: E402,E501
from dpia_generator_p2 import RISK_CATEGORIES  # noqa: E402,E501
# fmt: on


def assess_dpia_requirement(input_data: Dict) -> Dict:
    """Assess whether DPIA is required based on triggers."""
    triggers_present = input_data.get("dpia_triggers", [])
    total_weight = 0
    triggered_criteria = []

    for trigger in triggers_present:
        if trigger in DPIA_TRIGGERS:
            trigger_info = DPIA_TRIGGERS[trigger]
            total_weight += trigger_info["weight"]
            triggered_criteria.append({
                "trigger": trigger,
                "description": trigger_info["description"],
                "article": trigger_info["article"]
            })

    # Also check data characteristics
    if input_data.get("data_subjects", {}).get("vulnerable_groups"):
        if "vulnerable_subjects" not in triggers_present:
            total_weight += DPIA_TRIGGERS["vulnerable_subjects"]["weight"]
            triggered_criteria.append({
                "trigger": "vulnerable_subjects",
                "description": DPIA_TRIGGERS["vulnerable_subjects"]["description"],
                "article": DPIA_TRIGGERS["vulnerable_subjects"]["article"]
            })

    if input_data.get("personal_data", {}).get("special_categories"):
        if "sensitive_data" not in triggers_present:
            total_weight += DPIA_TRIGGERS["sensitive_data"]["weight"]
            triggered_criteria.append({
                "trigger": "sensitive_data",
                "description": DPIA_TRIGGERS["sensitive_data"]["description"],
                "article": DPIA_TRIGGERS["sensitive_data"]["article"]
            })

    if input_data.get("data_recipients", {}).get("third_countries"):
        if "cross_border_transfer" not in triggers_present:
            total_weight += DPIA_TRIGGERS["cross_border_transfer"]["weight"]
            triggered_criteria.append({
                "trigger": "cross_border_transfer",
                "description": DPIA_TRIGGERS["cross_border_transfer"]["description"],
                "article": DPIA_TRIGGERS["cross_border_transfer"]["article"]
            })

    # DPIA required if 2+ triggers or weight >= 10
    dpia_required = len(triggered_criteria) >= 2 or total_weight >= 10

    return {
        "dpia_required": dpia_required,
        "risk_score": total_weight,
        "triggered_criteria": triggered_criteria,
        "recommendation": "DPIA is mandatory" if dpia_required else "DPIA recommended as best practice"
    }
def assess_risks(input_data: Dict) -> List[Dict]:
    """Assess risks based on processing characteristics."""
    risks = []

    # Check each risk category
    processing = input_data.get("processing_operations", {})
    recipients = input_data.get("data_recipients", {})
    personal_data = input_data.get("personal_data", {})

    # Unauthorized access risk
    if processing.get("storage_location") or processing.get("collection_method"):
        risks.append({
            **RISK_CATEGORIES["unauthorized_access"],
            "likelihood": "medium",
            "residual_risk": "low" if processing.get("access_controls") else "medium"
        })

    # Data breach risk (always present)
    risks.append({
        **RISK_CATEGORIES["data_breach"],
        "likelihood": "medium",
        "residual_risk": "medium"
    })

    # Third party risk
    if recipients.get("external_processors") or recipients.get("third_countries"):
        risks.append({
            **RISK_CATEGORIES["third_party_risk"],
            "likelihood": "medium",
            "residual_risk": "medium"
        })

    # Rights violation risk
    risks.append({
        **RISK_CATEGORIES["rights_violation"],
        "likelihood": "low",
        "residual_risk": "low"
    })

    # Retention violation risk
    if not personal_data.get("retention_period"):
        risks.append({
            **RISK_CATEGORIES["retention_violation"],
            "likelihood": "high",
            "residual_risk": "high"
        })

    # Automated decision risk
    if processing.get("automated_decisions") or processing.get("profiling"):
        risks.append({
            "description": "Risk of unfair automated decisions affecting individuals",
            "impact": "high",
            "likelihood": "medium",
            "residual_risk": "medium",
            "mitigations": [
                "Human review of automated decisions",
                "Transparency about logic involved",
                "Right to contest decisions",
                "Regular algorithm audits"
            ]
        })

    return risks

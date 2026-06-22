# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_calculator_base import *  # noqa: F403,E402


PROBABILITY_LEVELS = {
    1: {"name": "Improbable", "description": "Very unlikely to occur", "frequency": "<10^-6"},
    2: {"name": "Remote", "description": "Unlikely to occur", "frequency": "10^-5 to 10^-6"},
    3: {"name": "Occasional", "description": "May occur", "frequency": "10^-4 to 10^-5"},
    4: {"name": "Probable", "description": "Likely to occur", "frequency": "10^-3 to 10^-4"},
    5: {"name": "Frequent", "description": "Expected to occur", "frequency": ">10^-3"}
}
SEVERITY_LEVELS = {
    1: {"name": "Negligible", "description": "Inconvenience or temporary discomfort", "harm": "No injury"},
    2: {"name": "Minor", "description": "Temporary injury not requiring intervention", "harm": "Temporary discomfort"},
    3: {"name": "Serious", "description": "Injury requiring professional intervention", "harm": "Reversible injury"},
    4: {"name": "Critical", "description": "Permanent impairment or life-threatening", "harm": "Permanent impairment"},
    5: {"name": "Catastrophic", "description": "Death", "harm": "Death"}
}
RISK_MATRIX = {
    1: {1: "Low", 2: "Low", 3: "Low", 4: "Medium", 5: "Medium"},
    2: {1: "Low", 2: "Low", 3: "Medium", 4: "Medium", 5: "High"},
    3: {1: "Low", 2: "Medium", 3: "Medium", 4: "High", 5: "High"},
    4: {1: "Medium", 2: "Medium", 3: "High", 4: "High", 5: "Unacceptable"},
    5: {1: "Medium", 2: "High", 3: "High", 4: "Unacceptable", 5: "Unacceptable"}
}
RISK_ACTIONS = {
    "Low": {
        "acceptable": True,
        "action": "Document and accept. No further action required.",
        "color": "green"
    },
    "Medium": {
        "acceptable": "ALARP",
        "action": "Reduce risk if practicable. Document ALARP rationale if not reduced.",
        "color": "yellow"
    },
    "High": {
        "acceptable": "ALARP",
        "action": "Risk reduction required. Must demonstrate ALARP if residual risk remains high.",
        "color": "orange"
    },
    "Unacceptable": {
        "acceptable": False,
        "action": "Risk reduction mandatory. Design change required before proceeding.",
        "color": "red"
    }
}
FMEA_SEVERITY = {
    1: "No effect",
    2: "Very minor effect",
    3: "Minor effect",
    4: "Very low effect",
    5: "Low effect",
    6: "Moderate effect",
    7: "High effect",
    8: "Very high effect",
    9: "Hazardous with warning",
    10: "Hazardous without warning"
}
FMEA_OCCURRENCE = {
    1: "Remote (<1 in 1,500,000)",
    2: "Very low (1 in 150,000)",
    3: "Low (1 in 15,000)",
    4: "Moderately low (1 in 2,000)",
    5: "Moderate (1 in 400)",
    6: "Moderately high (1 in 80)",
    7: "High (1 in 20)",
    8: "Very high (1 in 8)",
    9: "Extremely high (1 in 3)",
    10: "Almost certain (>1 in 2)"
}
FMEA_DETECTION = {
    1: "Almost certain detection",
    2: "Very high detection",
    3: "High detection",
    4: "Moderately high detection",
    5: "Moderate detection",
    6: "Low detection",
    7: "Very low detection",
    8: "Remote detection",
    9: "Very remote detection",
    10: "Cannot detect"
}
def calculate_risk_level(probability: int, severity: int) -> dict:
    """Calculate risk level from probability and severity ratings."""
    if probability < 1 or probability > 5:
        return {"error": f"Probability must be 1-5, got {probability}"}
    if severity < 1 or severity > 5:
        return {"error": f"Severity must be 1-5, got {severity}"}

    risk_level = RISK_MATRIX[probability][severity]
    risk_info = RISK_ACTIONS[risk_level]

    return {
        "probability": {
            "rating": probability,
            **PROBABILITY_LEVELS[probability]
        },
        "severity": {
            "rating": severity,
            **SEVERITY_LEVELS[severity]
        },
        "risk_level": risk_level,
        "acceptable": risk_info["acceptable"],
        "action_required": risk_info["action"],
        "risk_index": probability * severity
    }

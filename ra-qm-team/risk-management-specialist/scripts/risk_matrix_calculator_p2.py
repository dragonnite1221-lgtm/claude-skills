# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_calculator_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_calculator_p1 import FMEA_DETECTION, FMEA_OCCURRENCE, FMEA_SEVERITY, PROBABILITY_LEVELS, RISK_ACTIONS, RISK_MATRIX, SEVERITY_LEVELS  # noqa: E402,E501
# fmt: on


def calculate_rpn(severity: int, occurrence: int, detection: int) -> dict:
    """Calculate FMEA Risk Priority Number."""
    if not all(1 <= x <= 10 for x in [severity, occurrence, detection]):
        return {"error": "All FMEA ratings must be 1-10"}

    rpn = severity * occurrence * detection

    # Determine priority level
    if rpn > 200:
        priority = "Critical"
        action = "Immediate action required"
    elif rpn > 100:
        priority = "High"
        action = "Action plan required"
    elif rpn > 50:
        priority = "Medium"
        action = "Consider risk reduction"
    else:
        priority = "Low"
        action = "Monitor"

    return {
        "severity": {
            "rating": severity,
            "description": FMEA_SEVERITY[severity]
        },
        "occurrence": {
            "rating": occurrence,
            "description": FMEA_OCCURRENCE[occurrence]
        },
        "detection": {
            "rating": detection,
            "description": FMEA_DETECTION[detection]
        },
        "rpn": rpn,
        "priority": priority,
        "action_required": action,
        "max_rpn": 1000,
        "rpn_percentage": round(rpn / 10, 1)
    }
def display_risk_matrix():
    """Display the full risk matrix."""
    print("\n" + "=" * 70)
    print("ISO 14971 RISK MATRIX (5x5)")
    print("=" * 70)

    # Header
    print("\n" + " " * 15, end="")
    for s in range(1, 6):
        print(f"S{s:^10}", end="")
    print()

    print(" " * 15, end="")
    for s in range(1, 6):
        print(f"{SEVERITY_LEVELS[s]['name'][:10]:^10}", end="")
    print()

    print("-" * 70)

    # Matrix rows
    for p in range(5, 0, -1):
        print(f"P{p} {PROBABILITY_LEVELS[p]['name'][:10]:>10} |", end="")
        for s in range(1, 6):
            level = RISK_MATRIX[p][s]
            print(f"{level:^10}", end="")
        print()

    print("\n" + "-" * 70)
    print("Risk Levels: Low (Acceptable) | Medium (ALARP) | High (ALARP) | Unacceptable")
    print("=" * 70)
def display_criteria():
    """Display probability and severity criteria."""
    print("\n" + "=" * 70)
    print("PROBABILITY CRITERIA")
    print("=" * 70)
    for level, info in PROBABILITY_LEVELS.items():
        print(f"\nP{level}: {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Frequency: {info['frequency']}")

    print("\n" + "=" * 70)
    print("SEVERITY CRITERIA")
    print("=" * 70)
    for level, info in SEVERITY_LEVELS.items():
        print(f"\nS{level}: {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Harm: {info['harm']}")

    print("\n" + "=" * 70)
    print("RISK LEVEL ACTIONS")
    print("=" * 70)
    for level, info in RISK_ACTIONS.items():
        acceptable = "Yes" if info['acceptable'] == True else ("ALARP" if info['acceptable'] == "ALARP" else "No")
        print(f"\n{level}:")
        print(f"   Acceptable: {acceptable}")
        print(f"   Action: {info['action']}")

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_matrix_scorer_base import *  # noqa: F403,E402
# fmt: off
from decision_matrix_scorer_p1 import hr  # noqa: E402,E501
from decision_matrix_scorer_p2 import print_report  # noqa: E402,E501
# fmt: on


def interactive_mode():
    """Guided interactive data entry."""
    print()
    print(hr("═"))
    print("  DECISION MATRIX — Interactive Mode")
    print(hr("═"))
    
    data = {}
    data["decision"] = input("\nWhat decision are you making?\n> ").strip()
    
    # Criteria
    print("\nDefine criteria (what matters in this decision).")
    print("Enter criteria one at a time. Empty line to finish.")
    print("Weight: importance 0–10 (will be normalized to %).")
    print()
    
    criteria = []
    while True:
        name = input(f"Criterion {len(criteria)+1} name (or ENTER to finish): ").strip()
        if not name:
            if len(criteria) < 2:
                print("  Need at least 2 criteria.")
                continue
            break
        weight_str = input(f"  Weight for '{name}' (0–10): ").strip()
        try:
            weight = float(weight_str)
        except ValueError:
            weight = 5.0
        criteria.append({"name": name, "weight": weight})
    
    data["criteria"] = criteria
    
    # Options
    print("\nDefine options (what you're choosing between).")
    print("Enter options one at a time. Empty line to finish.")
    print()
    
    options = []
    while True:
        name = input(f"Option {len(options)+1} name (or ENTER to finish): ").strip()
        if not name:
            if len(options) < 2:
                print("  Need at least 2 options.")
                continue
            break
        
        print(f"\n  Score each criterion for '{name}' (1=poor, 10=excellent):")
        scores = {}
        for c in criteria:
            while True:
                s = input(f"    {c['name']}: ").strip()
                try:
                    score = float(s)
                    if 1 <= score <= 10:
                        scores[c["name"]] = score
                        break
                    else:
                        print("    Score must be 1–10")
                except ValueError:
                    print("    Enter a number 1–10")
        
        options.append({"name": name, "scores": scores})
        print()
    
    data["options"] = options
    print_report(data)

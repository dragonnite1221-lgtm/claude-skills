# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_calculator_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_calculator_p1 import calculate_risk_level  # noqa: E402,E501
from risk_matrix_calculator_p2 import calculate_rpn, display_criteria, display_risk_matrix  # noqa: E402,E501
# fmt: on


def format_result_text(result: dict, analysis_type: str) -> str:
    """Format result for text output."""
    lines = []
    lines.append("\n" + "=" * 50)

    if analysis_type == "risk":
        lines.append("RISK ASSESSMENT RESULT")
        lines.append("=" * 50)
        lines.append(f"\nProbability: P{result['probability']['rating']} - {result['probability']['name']}")
        lines.append(f"  {result['probability']['description']}")
        lines.append(f"\nSeverity: S{result['severity']['rating']} - {result['severity']['name']}")
        lines.append(f"  {result['severity']['description']}")
        lines.append(f"\n{'-' * 50}")
        lines.append(f"RISK LEVEL: {result['risk_level']}")
        lines.append(f"Risk Index: {result['risk_index']} (P × S)")
        lines.append(f"Acceptable: {result['acceptable']}")
        lines.append(f"\nAction Required:")
        lines.append(f"  {result['action_required']}")

    elif analysis_type == "fmea":
        lines.append("FMEA RPN CALCULATION")
        lines.append("=" * 50)
        lines.append(f"\nSeverity: {result['severity']['rating']}/10")
        lines.append(f"  {result['severity']['description']}")
        lines.append(f"\nOccurrence: {result['occurrence']['rating']}/10")
        lines.append(f"  {result['occurrence']['description']}")
        lines.append(f"\nDetection: {result['detection']['rating']}/10")
        lines.append(f"  {result['detection']['description']}")
        lines.append(f"\n{'-' * 50}")
        lines.append(f"RPN: {result['rpn']} / {result['max_rpn']} ({result['rpn_percentage']}%)")
        lines.append(f"Priority: {result['priority']}")
        lines.append(f"\nAction Required:")
        lines.append(f"  {result['action_required']}")

    lines.append("=" * 50)
    return "\n".join(lines)
def interactive_mode():
    """Run interactive risk assessment."""
    print("\n" + "=" * 50)
    print("RISK MATRIX CALCULATOR - Interactive Mode")
    print("=" * 50)

    print("\nSelect analysis type:")
    print("1. Risk Matrix (ISO 14971 style)")
    print("2. FMEA RPN Calculation")
    print("3. Display Risk Matrix")
    print("4. Display Criteria")
    print("5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        display_criteria()
        print("\n" + "-" * 50)
        try:
            p = int(input("Enter Probability (1-5): "))
            s = int(input("Enter Severity (1-5): "))
            result = calculate_risk_level(p, s)
            if "error" in result:
                print(f"\nError: {result['error']}")
            else:
                print(format_result_text(result, "risk"))
        except ValueError:
            print("Invalid input. Please enter numbers.")

    elif choice == "2":
        print("\nFMEA Scales:")
        print("  Severity: 1 (No effect) to 10 (Hazardous without warning)")
        print("  Occurrence: 1 (Remote) to 10 (Almost certain)")
        print("  Detection: 1 (Almost certain) to 10 (Cannot detect)")
        print("-" * 50)
        try:
            s = int(input("Enter Severity (1-10): "))
            o = int(input("Enter Occurrence (1-10): "))
            d = int(input("Enter Detection (1-10): "))
            result = calculate_rpn(s, o, d)
            if "error" in result:
                print(f"\nError: {result['error']}")
            else:
                print(format_result_text(result, "fmea"))
        except ValueError:
            print("Invalid input. Please enter numbers.")

    elif choice == "3":
        display_risk_matrix()

    elif choice == "4":
        display_criteria()

    elif choice == "5":
        print("Exiting.")
        return

    else:
        print("Invalid choice.")

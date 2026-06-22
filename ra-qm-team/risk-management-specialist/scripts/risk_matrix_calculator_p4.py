# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_calculator_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_calculator_p1 import calculate_risk_level  # noqa: E402,E501
from risk_matrix_calculator_p2 import calculate_rpn, display_criteria, display_risk_matrix  # noqa: E402,E501
from risk_matrix_calculator_p3 import format_result_text, interactive_mode  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Calculate risk levels per ISO 14971 or FMEA RPN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # ISO 14971 risk matrix calculation
  python risk_matrix_calculator.py --probability 3 --severity 4

  # FMEA RPN calculation
  python risk_matrix_calculator.py --fmea --severity 8 --occurrence 5 --detection 6

  # Interactive mode
  python risk_matrix_calculator.py --interactive

  # Display risk matrix
  python risk_matrix_calculator.py --show-matrix

  # Display criteria definitions
  python risk_matrix_calculator.py --list-criteria

  # JSON output
  python risk_matrix_calculator.py -p 4 -s 3 --output json
        """
    )

    parser.add_argument("-p", "--probability", type=int, help="Probability rating (1-5)")
    parser.add_argument("-s", "--severity", type=int, help="Severity rating (1-5 for risk, 1-10 for FMEA)")
    parser.add_argument("-o", "--occurrence", type=int, help="FMEA occurrence rating (1-10)")
    parser.add_argument("-d", "--detection", type=int, help="FMEA detection rating (1-10)")
    parser.add_argument("--fmea", action="store_true", help="Use FMEA RPN calculation")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--show-matrix", action="store_true", help="Display risk matrix")
    parser.add_argument("--list-criteria", action="store_true", help="Display probability and severity criteria")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.show_matrix:
        display_risk_matrix()
        return

    if args.list_criteria:
        display_criteria()
        return

    if args.fmea:
        if not all([args.severity, args.occurrence, args.detection]):
            parser.error("FMEA requires --severity, --occurrence, and --detection")

        result = calculate_rpn(args.severity, args.occurrence, args.detection)
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            print(format_result_text(result, "fmea"))

    else:
        if not all([args.probability, args.severity]):
            parser.error("Risk calculation requires --probability and --severity")

        result = calculate_risk_level(args.probability, args.severity)
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            print(format_result_text(result, "risk"))

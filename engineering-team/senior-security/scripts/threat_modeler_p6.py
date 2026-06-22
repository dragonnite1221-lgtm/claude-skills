# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402
# fmt: off
from threat_modeler_p4 import get_threats_for_component  # noqa: E402,E501
from threat_modeler_p5 import format_json_report, format_threat_report, interactive_mode, list_all_threats  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="STRIDE Threat Modeler - Analyze security threats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze authentication component
  python threat_modeler.py --component "User Authentication"

  # Analyze with specific assets
  python threat_modeler.py --component "API Gateway" --assets "user_data,tokens"

  # JSON output for integration
  python threat_modeler.py --component "Database" --json

  # Interactive mode
  python threat_modeler.py --interactive

  # List all threats in database
  python threat_modeler.py --list-threats
        """
    )

    parser.add_argument(
        "--component", "-c",
        help="Component to analyze (e.g., 'User Authentication', 'API Gateway')"
    )
    parser.add_argument(
        "--assets", "-a",
        help="Comma-separated list of assets to protect"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--list-threats", "-l",
        action="store_true",
        help="List all threats in database"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.list_threats:
        list_all_threats()
        return

    if not args.component:
        parser.error("--component is required (or use --interactive)")

    threats = get_threats_for_component(args.component)

    if args.json:
        output = json.dumps(format_json_report(args.component, threats), indent=2)
    else:
        output = format_threat_report(args.component, threats)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

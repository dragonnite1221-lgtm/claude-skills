# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from severity_classifier_base import *  # noqa: F403,E402
# fmt: off
from severity_classifier_p1 import SeverityLevel  # noqa: E402,E501
from severity_classifier_p3 import parse_incident_data  # noqa: E402,E501
from severity_classifier_p4 import classify_severity  # noqa: E402,E501
from severity_classifier_p5 import build_escalation_path  # noqa: E402,E501
from severity_classifier_p6 import build_action_plan  # noqa: E402,E501
from severity_classifier_p7 import assess_sla_impact  # noqa: E402,E501
from severity_classifier_p8 import format_text  # noqa: E402,E501
from severity_classifier_p9 import format_json  # noqa: E402,E501
from severity_classifier_p10 import format_markdown  # noqa: E402,E501
# fmt: on


def main() -> None:
    """Parse arguments, read input, classify, and emit output."""
    parser = argparse.ArgumentParser(
        description="Classify incident severity and generate escalation paths.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s incident.json
  %(prog)s incident.json --format json
  %(prog)s incident.json --format markdown
  cat incident.json | %(prog)s
  cat incident.json | %(prog)s --format json
""",
    )

    parser.add_argument(
        "data_file",
        nargs="?",
        default=None,
        help="JSON file with incident data (reads stdin if omitted)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # -- Read input --
    try:
        if args.data_file:
            with open(args.data_file, "r", encoding="utf-8") as fh:
                raw_data = json.load(fh)
        else:
            if sys.stdin.isatty():
                parser.error("No input file provided and stdin is a terminal. Pipe JSON or pass a file.")
            raw_data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON input -- {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: file not found -- {args.data_file}", file=sys.stderr)
        sys.exit(1)
    except IOError as exc:
        print(f"Error: could not read input -- {exc}", file=sys.stderr)
        sys.exit(1)

    # -- Parse and validate --
    try:
        incident, impact, signals, context = parse_incident_data(raw_data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # -- Classify --
    severity_score = classify_severity(incident, impact, signals, context)

    # -- Build outputs --
    escalation = build_escalation_path(severity_score, signals, context)
    action_plan = build_action_plan(severity_score, incident, impact, signals, context)
    sla_impact = assess_sla_impact(severity_score, impact, signals)

    # -- Format and print --
    if args.output_format == "json":
        output = format_json(incident, severity_score, escalation, action_plan, sla_impact)
    elif args.output_format == "markdown":
        output = format_markdown(incident, severity_score, escalation, action_plan, sla_impact)
    else:
        output = format_text(incident, severity_score, escalation, action_plan, sla_impact)

    print(output)

    # -- Exit code reflects severity --
    if severity_score.severity_level == SeverityLevel.SEV1:
        sys.exit(2)
    elif severity_score.severity_level == SeverityLevel.SEV2:
        sys.exit(1)
    else:
        sys.exit(0)

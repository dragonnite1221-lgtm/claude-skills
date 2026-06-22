# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402
from pir_generator_p0 import format_json_output, format_markdown_output, format_text_output  # noqa: F401,E501


def main():
    """Main function with argument parsing and execution."""
    parser = argparse.ArgumentParser(
        description="Generate Post-Incident Review documents with RCA and action items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pir_generator.py --incident incident.json --output pir.md
  python pir_generator.py --incident incident.json --rca-method fishbone
  cat incident.json | python pir_generator.py --format markdown
  
Incident JSON format:
  {
    "incident_id": "INC-2024-001",
    "title": "Database performance degradation",
    "description": "Users experiencing slow response times",
    "severity": "sev2",
    "start_time": "2024-01-01T12:00:00Z",
    "end_time": "2024-01-01T14:30:00Z",
    "customer_impact": "50% of users affected by slow page loads",
    "business_impact": "Moderate user experience degradation",
    "incident_commander": "Alice Smith",
    "responders": ["Bob Jones", "Carol Johnson"]
  }
        """
    )
    
    parser.add_argument(
        "--incident", "-i",
        help="Incident data file (JSON) or '-' for stdin"
    )
    
    parser.add_argument(
        "--timeline", "-t",
        help="Timeline reconstruction file (JSON)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "text"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--rca-method",
        choices=["five_whys", "fishbone", "timeline", "bow_tie"],
        default="five_whys",
        help="Root cause analysis method (default: five_whys)"
    )
    
    parser.add_argument(
        "--template-type",
        choices=["comprehensive", "standard", "brief"],
        default="comprehensive",
        help="PIR template type (default: comprehensive)"
    )
    
    parser.add_argument(
        "--action-items",
        action="store_true",
        help="Generate detailed action items"
    )
    
    args = parser.parse_args()
    
    generator = PIRGenerator()
    
    try:
        # Read incident data
        if args.incident == "-" or (not args.incident and not sys.stdin.isatty()):
            # Read from stdin
            input_text = sys.stdin.read().strip()
            if not input_text:
                parser.error("No incident data provided")
            incident_data = json.loads(input_text)
        elif args.incident:
            # Read from file
            with open(args.incident, 'r') as f:
                incident_data = json.load(f)
        else:
            parser.error("No incident data specified. Use --incident or pipe data to stdin.")
        
        # Read timeline data if provided
        timeline_data = None
        if args.timeline:
            with open(args.timeline, 'r') as f:
                timeline_data = json.load(f)
        
        # Validate incident data
        if not isinstance(incident_data, dict):
            parser.error("Incident data must be a JSON object")
        
        if not incident_data.get("description") and not incident_data.get("title"):
            parser.error("Incident data must contain 'description' or 'title'")
        
        # Generate PIR
        result = generator.generate_pir(
            incident_data=incident_data,
            timeline_data=timeline_data,
            rca_method=args.rca_method,
            template_type=args.template_type
        )
        
        # Format output
        if args.format == "json":
            output = format_json_output(result)
        elif args.format == "markdown":
            output = format_markdown_output(result)
        else:
            output = format_text_output(result)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
                f.write('\n')
        else:
            print(output)
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

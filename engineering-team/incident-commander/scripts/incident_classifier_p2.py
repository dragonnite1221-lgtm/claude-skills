# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402
from incident_classifier_p0 import format_json_output, format_text_output, parse_input_text  # noqa: F401,E501
from incident_classifier_p1 import interactive_mode  # noqa: F401,E501


def main():
    """Main function with argument parsing and execution."""
    parser = argparse.ArgumentParser(
        description="Classify incidents and provide response recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python incident_classifier.py --input incident.json
  echo "Database is down" | python incident_classifier.py --format text
  python incident_classifier.py --interactive
  
Input JSON format:
  {
    "description": "Database connection timeouts",
    "service": "user-service",
    "affected_users": "80%",
    "business_impact": "high"
  }
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input file path (JSON format) or '-' for stdin"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    classifier = IncidentClassifier()
    
    try:
        # Read input
        if args.input == "-" or (not args.input and not sys.stdin.isatty()):
            # Read from stdin
            input_text = sys.stdin.read().strip()
            if not input_text:
                parser.error("No input provided")
            
            # Try to parse as JSON first, then as text
            try:
                incident_data = json.loads(input_text)
            except json.JSONDecodeError:
                incident_data = parse_input_text(input_text)
                
        elif args.input:
            # Read from file
            with open(args.input, 'r') as f:
                incident_data = json.load(f)
        else:
            parser.error("No input specified. Use --input, --interactive, or pipe data to stdin.")
        
        # Validate required fields
        if not isinstance(incident_data, dict):
            parser.error("Input must be a JSON object")
        
        if "description" not in incident_data:
            parser.error("Input must contain 'description' field")
        
        # Classify incident
        result = classifier.classify_incident(incident_data)
        
        # Format output
        if args.format == "json":
            output = format_json_output(result)
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

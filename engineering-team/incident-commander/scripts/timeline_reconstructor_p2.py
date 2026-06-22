# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402
from timeline_reconstructor_p0 import format_json_output, format_text_output  # noqa: F401,E501
from timeline_reconstructor_p1 import format_markdown_output  # noqa: F401,E501


def main():
    """Main function with argument parsing and execution."""
    parser = argparse.ArgumentParser(
        description="Reconstruct incident timeline from timestamped events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python timeline_reconstructor.py --input events.json --output timeline.md
  python timeline_reconstructor.py --input events.json --detect-phases --gap-analysis
  cat events.json | python timeline_reconstructor.py --format text
  
Input JSON format:
  [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "source": "monitoring",
      "type": "alert",
      "message": "High error rate detected",
      "severity": "critical",
      "actor": "system"
    }
  ]
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input file path (JSON format) or '-' for stdin"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "markdown"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--detect-phases",
        action="store_true",
        help="Enable advanced phase detection"
    )
    
    parser.add_argument(
        "--gap-analysis",
        action="store_true",
        help="Perform gap analysis on timeline"
    )
    
    parser.add_argument(
        "--min-events",
        type=int,
        default=1,
        help="Minimum number of events required (default: 1)"
    )
    
    args = parser.parse_args()
    
    reconstructor = TimelineReconstructor()
    
    try:
        # Read input
        if args.input == "-" or (not args.input and not sys.stdin.isatty()):
            # Read from stdin
            input_text = sys.stdin.read().strip()
            if not input_text:
                parser.error("No input provided")
            events_data = json.loads(input_text)
        elif args.input:
            # Read from file
            with open(args.input, 'r') as f:
                events_data = json.load(f)
        else:
            parser.error("No input specified. Use --input or pipe data to stdin.")
        
        # Validate input
        if not isinstance(events_data, list):
            parser.error("Input must be a JSON array of events")
        
        if len(events_data) < args.min_events:
            parser.error(f"Minimum {args.min_events} events required")
        
        # Reconstruct timeline
        result = reconstructor.reconstruct_timeline(events_data)
        
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

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare API specification versions to detect breaking changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python breaking_change_detector.py v1.json v2.json
  python breaking_change_detector.py --format json v1.json v2.json > changes.json
  python breaking_change_detector.py --output report.txt v1.json v2.json
        """
    )
    
    parser.add_argument(
        'old_spec',
        help='Old API specification file (JSON format)'
    )
    
    parser.add_argument(
        'new_spec',
        help='New API specification file (JSON format)'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--exit-on-breaking',
        action='store_true',
        help='Exit with code 1 if breaking changes are detected'
    )
    
    args = parser.parse_args()
    
    # Load specification files
    try:
        with open(args.old_spec, 'r') as f:
            old_spec = json.load(f)
    except FileNotFoundError:
        print(f"Error: Old specification file '{args.old_spec}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.old_spec}': {e}", file=sys.stderr)
        return 1
    
    try:
        with open(args.new_spec, 'r') as f:
            new_spec = json.load(f)
    except FileNotFoundError:
        print(f"Error: New specification file '{args.new_spec}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.new_spec}': {e}", file=sys.stderr)
        return 1
    
    # Initialize detector and compare specifications
    detector = BreakingChangeDetector()
    
    try:
        report = detector.compare_specs(old_spec, new_spec)
    except Exception as e:
        print(f"Error during comparison: {e}", file=sys.stderr)
        return 1
    
    # Generate report
    if args.format == 'json':
        output = detector.generate_json_report()
    else:
        output = detector.generate_text_report()
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Breaking change report written to {args.output}")
        except IOError as e:
            print(f"Error writing to '{args.output}': {e}", file=sys.stderr)
            return 1
    else:
        print(output)
    
    # Exit with appropriate code
    if args.exit_on_breaking and report.has_breaking_changes():
        return 1
    
    return 0

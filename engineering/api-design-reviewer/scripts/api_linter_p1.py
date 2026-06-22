# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze OpenAPI/Swagger specifications for REST conventions and best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_linter.py openapi.json
  python api_linter.py --format json openapi.json > report.json
  python api_linter.py --raw-endpoints endpoints.json
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input file: OpenAPI/Swagger JSON file or raw endpoints JSON'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--raw-endpoints',
        action='store_true',
        help='Treat input as raw endpoint definitions instead of OpenAPI spec'
    )
    
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Load input file
    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.input_file}': {e}", file=sys.stderr)
        return 1
    
    # Initialize linter and run analysis
    linter = APILinter()
    
    try:
        if args.raw_endpoints:
            report = linter.lint_raw_endpoints(input_data)
        else:
            report = linter.lint_openapi_spec(input_data)
    except Exception as e:
        print(f"Error during linting: {e}", file=sys.stderr)
        return 1
    
    # Generate report
    if args.format == 'json':
        output = linter.generate_json_report()
    else:
        output = linter.generate_text_report()
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Report written to {args.output}")
        except IOError as e:
            print(f"Error writing to '{args.output}': {e}", file=sys.stderr)
            return 1
    else:
        print(output)
    
    # Return appropriate exit code
    error_count = len([i for i in report.issues if i.severity == 'error'])
    return 1 if error_count > 0 else 0

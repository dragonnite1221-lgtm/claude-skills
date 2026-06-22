# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive API design quality scorecard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_scorecard.py openapi.json
  python api_scorecard.py --format json openapi.json > scorecard.json
  python api_scorecard.py --output scorecard.txt openapi.json
        """
    )
    
    parser.add_argument(
        'spec_file',
        help='OpenAPI/Swagger specification file (JSON format)'
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
        '--min-grade',
        choices=['A', 'B', 'C', 'D', 'F'],
        help='Exit with code 1 if grade is below minimum'
    )
    
    args = parser.parse_args()
    
    # Load specification file
    try:
        with open(args.spec_file, 'r') as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"Error: Specification file '{args.spec_file}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.spec_file}': {e}", file=sys.stderr)
        return 1
    
    # Initialize scoring engine and generate scorecard
    engine = APIScoringEngine()
    
    try:
        scorecard = engine.score_api(spec)
    except Exception as e:
        print(f"Error during scoring: {e}", file=sys.stderr)
        return 1
    
    # Generate report
    if args.format == 'json':
        output = engine.generate_json_report()
    else:
        output = engine.generate_text_report()
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Scorecard written to {args.output}")
        except IOError as e:
            print(f"Error writing to '{args.output}': {e}", file=sys.stderr)
            return 1
    else:
        print(output)
    
    # Check minimum grade requirement
    if args.min_grade:
        grade_order = ['F', 'D', 'C', 'B', 'A']
        current_grade_index = grade_order.index(scorecard.overall_grade)
        min_grade_index = grade_order.index(args.min_grade)
        
        if current_grade_index < min_grade_index:
            print(f"Grade {scorecard.overall_grade} is below minimum required grade {args.min_grade}", file=sys.stderr)
            return 1
    
    return 0

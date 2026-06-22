# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Analyze schema and API compatibility between versions")
    parser.add_argument("--before", required=True, help="Before schema file (JSON)")
    parser.add_argument("--after", required=True, help="After schema file (JSON)")
    parser.add_argument("--type", choices=["database", "api"], default="database", help="Schema type to analyze")
    parser.add_argument("--output", "-o", help="Output file for compatibility report (JSON)")
    parser.add_argument("--format", "-f", choices=["json", "text", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Load schemas
        with open(args.before, 'r') as f:
            before_schema = json.load(f)
        
        with open(args.after, 'r') as f:
            after_schema = json.load(f)
        
        # Analyze compatibility
        checker = SchemaCompatibilityChecker()
        
        if args.type == "database":
            report = checker.analyze_database_schema(before_schema, after_schema)
        else:  # api
            report = checker.analyze_api_schema(before_schema, after_schema)
        
        # Output results
        if args.format in ["json", "both"]:
            report_dict = asdict(report)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report_dict, f, indent=2)
                print(f"Compatibility report saved to {args.output}")
            else:
                print(json.dumps(report_dict, indent=2))
        
        if args.format in ["text", "both"]:
            human_report = checker.generate_human_readable_report(report)
            text_output = args.output.replace('.json', '.txt') if args.output else None
            if text_output:
                with open(text_output, 'w') as f:
                    f.write(human_report)
                print(f"Human-readable report saved to {text_output}")
            else:
                print("\n" + "="*80)
                print("HUMAN-READABLE COMPATIBILITY REPORT")
                print("="*80)
                print(human_report)
        
        # Return exit code based on compatibility
        if report.breaking_changes_count > 0:
            return 2  # Breaking changes found
        elif report.potentially_breaking_count > 0:
            return 1  # Potentially breaking changes found
        else:
            return 0  # No compatibility issues
            
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

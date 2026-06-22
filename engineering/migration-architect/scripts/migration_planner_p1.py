# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Generate comprehensive migration plans")
    parser.add_argument("--input", "-i", required=True, help="Input migration specification file (JSON)")
    parser.add_argument("--output", "-o", help="Output file for migration plan (JSON)")
    parser.add_argument("--format", "-f", choices=["json", "text", "both"], default="both",
                       help="Output format")
    parser.add_argument("--validate", action="store_true", help="Validate migration specification only")
    
    args = parser.parse_args()
    
    try:
        # Load migration specification
        with open(args.input, 'r') as f:
            spec = json.load(f)
        
        # Validate required fields
        required_fields = ["type", "source", "target"]
        for field in required_fields:
            if field not in spec:
                print(f"Error: Missing required field '{field}' in specification", file=sys.stderr)
                return 1
        
        if args.validate:
            print("Migration specification is valid")
            return 0
        
        # Generate migration plan
        planner = MigrationPlanner()
        plan = planner.generate_plan(spec)
        
        # Output results
        if args.format in ["json", "both"]:
            plan_dict = asdict(plan)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(plan_dict, f, indent=2)
                print(f"Migration plan saved to {args.output}")
            else:
                print(json.dumps(plan_dict, indent=2))
        
        if args.format in ["text", "both"]:
            human_plan = planner.generate_human_readable_plan(plan)
            text_output = args.output.replace('.json', '.txt') if args.output else None
            if text_output:
                with open(text_output, 'w') as f:
                    f.write(human_plan)
                print(f"Human-readable plan saved to {text_output}")
            else:
                print("\n" + "="*80)
                print("HUMAN-READABLE MIGRATION PLAN")
                print("="*80)
                print(human_plan)
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

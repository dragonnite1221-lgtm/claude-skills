# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Generate comprehensive rollback runbooks from migration plans")
    parser.add_argument("--input", "-i", required=True, help="Input migration plan file (JSON)")
    parser.add_argument("--output", "-o", help="Output file for rollback runbook (JSON)")
    parser.add_argument("--format", "-f", choices=["json", "text", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Load migration plan
        with open(args.input, 'r') as f:
            migration_plan = json.load(f)
        
        # Validate required fields
        if "migration_id" not in migration_plan and "source" not in migration_plan:
            print("Error: Migration plan must contain migration_id or source field", file=sys.stderr)
            return 1
        
        # Generate rollback runbook
        generator = RollbackGenerator()
        runbook = generator.generate_rollback_runbook(migration_plan)
        
        # Output results
        if args.format in ["json", "both"]:
            runbook_dict = asdict(runbook)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(runbook_dict, f, indent=2)
                print(f"Rollback runbook saved to {args.output}")
            else:
                print(json.dumps(runbook_dict, indent=2))
        
        if args.format in ["text", "both"]:
            human_runbook = generator.generate_human_readable_runbook(runbook)
            text_output = args.output.replace('.json', '.txt') if args.output else None
            if text_output:
                with open(text_output, 'w') as f:
                    f.write(human_runbook)
                print(f"Human-readable runbook saved to {text_output}")
            else:
                print("\n" + "="*80)
                print("HUMAN-READABLE ROLLBACK RUNBOOK")
                print("="*80)
                print(human_runbook)
        
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

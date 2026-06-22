# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402
from debt_prioritizer_p0 import format_prioritized_report  # noqa: F401,E501


def main():
    """Main entry point for the debt prioritizer."""
    parser = argparse.ArgumentParser(description="Prioritize technical debt backlog")
    parser.add_argument("inventory_file", help="Path to debt inventory JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "text", "both"], 
                       default="both", help="Output format")
    parser.add_argument("--framework", choices=["cost_of_delay", "wsjf", "rice"],
                       default="cost_of_delay", help="Prioritization framework")
    parser.add_argument("--team-size", type=int, default=5, help="Team size")
    parser.add_argument("--sprint-capacity", type=int, default=80, 
                       help="Sprint capacity in hours")
    
    args = parser.parse_args()
    
    # Initialize prioritizer
    prioritizer = DebtPrioritizer(args.team_size, args.sprint_capacity)
    
    # Load inventory
    if not prioritizer.load_debt_inventory(args.inventory_file):
        sys.exit(1)
    
    # Analyze and prioritize
    try:
        analysis_result = prioritizer.analyze_and_prioritize(args.framework)
    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)
    
    # Output results
    if args.format in ["json", "both"]:
        json_output = json.dumps(analysis_result, indent=2, default=str)
        if args.output:
            output_path = args.output if args.output.endswith('.json') else f"{args.output}.json"
            with open(output_path, 'w') as f:
                f.write(json_output)
            print(f"JSON report written to: {output_path}")
        else:
            print("JSON REPORT:")
            print("=" * 50)
            print(json_output)
    
    if args.format in ["text", "both"]:
        text_output = format_prioritized_report(analysis_result)
        if args.output:
            output_path = args.output if args.output.endswith('.txt') else f"{args.output}.txt"
            with open(output_path, 'w') as f:
                f.write(text_output)
            print(f"Text report written to: {output_path}")
        else:
            print("\nTEXT REPORT:")
            print("=" * 50)
            print(text_output)

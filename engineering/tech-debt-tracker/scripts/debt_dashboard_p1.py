# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402
from debt_dashboard_p0 import format_dashboard_report  # noqa: F401,E501


def main():
    """Main entry point for the debt dashboard."""
    parser = argparse.ArgumentParser(description="Generate technical debt dashboard")
    parser.add_argument("files", nargs="*", help="Debt inventory files")
    parser.add_argument("--input-dir", help="Directory containing debt inventory files")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "text", "both"], 
                       default="both", help="Output format")
    parser.add_argument("--period", choices=["weekly", "monthly", "quarterly"],
                       default="monthly", help="Analysis period")
    parser.add_argument("--team-size", type=int, default=5, help="Team size")
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = DebtDashboard(args.team_size)
    
    # Load data
    if args.input_dir:
        success = dashboard.load_from_directory(args.input_dir)
    elif args.files:
        success = dashboard.load_historical_data(args.files)
    else:
        print("Error: Must specify either files or --input-dir")
        sys.exit(1)
    
    if not success:
        sys.exit(1)
    
    # Generate dashboard
    try:
        dashboard_data = dashboard.generate_dashboard(args.period)
    except Exception as e:
        print(f"Dashboard generation failed: {e}")
        sys.exit(1)
    
    # Output results
    if args.format in ["json", "both"]:
        json_output = json.dumps(dashboard_data, indent=2, default=str)
        if args.output:
            output_path = args.output if args.output.endswith('.json') else f"{args.output}.json"
            with open(output_path, 'w') as f:
                f.write(json_output)
            print(f"JSON dashboard written to: {output_path}")
        else:
            print("JSON DASHBOARD:")
            print("=" * 50)
            print(json_output)
    
    if args.format in ["text", "both"]:
        text_output = format_dashboard_report(dashboard_data)
        if args.output:
            output_path = args.output if args.output.endswith('.txt') else f"{args.output}.txt"
            with open(output_path, 'w') as f:
                f.write(text_output)
            print(f"Text dashboard written to: {output_path}")
        else:
            print("\nTEXT DASHBOARD:")
            print("=" * 50)
            print(text_output)

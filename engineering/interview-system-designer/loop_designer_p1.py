# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402
from loop_designer_p0 import format_human_readable  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Generate calibrated interview loops for specific roles and levels")
    parser.add_argument("--role", type=str, help="Job role title (e.g., 'Senior Software Engineer')")
    parser.add_argument("--level", type=str, help="Experience level (junior, mid, senior, staff, principal)")
    parser.add_argument("--team", type=str, help="Team or department (optional)")
    parser.add_argument("--competencies", type=str, help="Comma-separated list of specific competencies to focus on")
    parser.add_argument("--input", type=str, help="Input JSON file with role definition")
    parser.add_argument("--output", type=str, help="Output directory or file path")
    parser.add_argument("--format", choices=["json", "text", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    designer = InterviewLoopDesigner()
    
    # Handle input
    if args.input:
        try:
            with open(args.input, 'r') as f:
                role_data = json.load(f)
            role = role_data.get('role') or role_data.get('title', '')
            level = role_data.get('level', 'senior')
            team = role_data.get('team')
            competencies = role_data.get('competencies')
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
    else:
        if not args.role or not args.level:
            print("Error: --role and --level are required when not using --input")
            sys.exit(1)
        
        role = args.role
        level = args.level
        team = args.team
        competencies = args.competencies.split(',') if args.competencies else None
    
    # Generate interview loop
    try:
        loop_data = designer.generate_interview_loop(role, level, team, competencies)
        
        # Handle output
        if args.output:
            output_path = args.output
            if os.path.isdir(output_path):
                safe_role = "".join(c for c in role.lower() if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                base_filename = f"{safe_role}_{level}_interview_loop"
                json_path = os.path.join(output_path, f"{base_filename}.json")
                text_path = os.path.join(output_path, f"{base_filename}.txt")
            else:
                # Use provided path as base
                json_path = output_path if output_path.endswith('.json') else f"{output_path}.json"
                text_path = output_path.replace('.json', '.txt') if output_path.endswith('.json') else f"{output_path}.txt"
        else:
            safe_role = "".join(c for c in role.lower() if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            base_filename = f"{safe_role}_{level}_interview_loop"
            json_path = f"{base_filename}.json"
            text_path = f"{base_filename}.txt"
        
        # Write outputs
        if args.format in ["json", "both"]:
            with open(json_path, 'w') as f:
                json.dump(loop_data, f, indent=2, default=str)
            print(f"JSON output written to: {json_path}")
        
        if args.format in ["text", "both"]:
            with open(text_path, 'w') as f:
                f.write(format_human_readable(loop_data))
            print(f"Text output written to: {text_path}")
        
        # Always print summary to stdout
        print("\nInterview Loop Summary:")
        print(f"Role: {loop_data['role']} ({loop_data['level'].title()})")
        print(f"Total Duration: {loop_data['total_duration_minutes']} minutes")
        print(f"Number of Rounds: {loop_data['total_rounds']}")
        print(f"Schedule Type: {loop_data['suggested_schedule']['type'].replace('_', ' ').title()}")
        
    except Exception as e:
        print(f"Error generating interview loop: {e}")
        sys.exit(1)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import SystemRequirements  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent System Architecture Planner")
    parser.add_argument("input_file", help="JSON file with system requirements")
    parser.add_argument("-o", "--output", help="Output file prefix (default: agent_architecture)")
    parser.add_argument("--format", choices=["json", "yaml", "both"], default="both", 
                       help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Load requirements
        with open(args.input_file, 'r') as f:
            requirements_data = json.load(f)
        
        requirements = SystemRequirements(**requirements_data)
        
        # Plan the system
        planner = AgentPlanner()
        design, mermaid_diagram, roadmap = planner.plan_system(requirements)
        
        # Prepare output
        output_data = {
            "architecture_design": asdict(design),
            "mermaid_diagram": mermaid_diagram,
            "implementation_roadmap": roadmap,
            "metadata": {
                "generated_by": "agent_planner.py",
                "requirements_file": args.input_file,
                "architecture_pattern": design.pattern.value,
                "agent_count": len(design.agents)
            }
        }
        
        # Output files
        output_prefix = args.output or "agent_architecture"
        
        if args.format in ["json", "both"]:
            with open(f"{output_prefix}.json", 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"JSON output written to {output_prefix}.json")
        
        if args.format in ["both"]:
            # Also create separate files for key components
            with open(f"{output_prefix}_diagram.mmd", 'w') as f:
                f.write(mermaid_diagram)
            print(f"Mermaid diagram written to {output_prefix}_diagram.mmd")
            
            with open(f"{output_prefix}_roadmap.json", 'w') as f:
                json.dump(roadmap, f, indent=2)
            print(f"Implementation roadmap written to {output_prefix}_roadmap.json")
        
        # Print summary
        print(f"\nArchitecture Summary:")
        print(f"Pattern: {design.pattern.value}")
        print(f"Agents: {len(design.agents)}")
        print(f"Communication Links: {len(design.communication_topology)}")
        print(f"Estimated Duration: {roadmap['total_duration']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

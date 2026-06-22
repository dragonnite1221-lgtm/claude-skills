# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p2 import CapacityAnalysisResult  # noqa: E402,E501
from resource_capacity_planner_p7 import analyze_capacity  # noqa: E402,E501
from resource_capacity_planner_p8 import format_text_output  # noqa: E402,E501
# fmt: on


def format_json_output(result: CapacityAnalysisResult) -> Dict[str, Any]:
    """Format analysis results as JSON."""
    # Helper function to serialize Resource objects
    def serialize_resource(resource):
        if hasattr(resource, 'id'):
            return {
                "id": resource.id,
                "name": resource.name,
                "role": resource.role,
                "utilization": resource.current_utilization,
                "available_hours": resource.available_hours,
                "hourly_rate": resource.hourly_rate
            }
        return resource
    
    # Deep copy and clean up the result
    serialized_result = {
        "summary": result.summary,
        "resource_analysis": result.resource_analysis,
        "project_analysis": result.project_analysis,
        "allocation_optimization": result.allocation_optimization,
        "scenario_analysis": result.scenario_analysis,
        "recommendations": result.recommendations
    }
    
    # Handle Resource objects in optimization suggestions
    if "suggested_reallocations" in serialized_result["allocation_optimization"]:
        for suggestion in serialized_result["allocation_optimization"]["suggested_reallocations"]:
            if "recommended_resources" in suggestion:
                for rec in suggestion["recommended_resources"]:
                    if "resource" in rec:
                        rec["resource"] = serialize_resource(rec["resource"])
    
    return serialized_result
def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze resource capacity and allocation across project portfolio"
    )
    parser.add_argument(
        "data_file", 
        help="JSON file containing resource and project capacity data"
    )
    parser.add_argument(
        "--format", 
        choices=["text", "json"], 
        default="text",
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load and validate data
        with open(args.data_file, 'r') as f:
            data = json.load(f)
        
        # Perform analysis
        result = analyze_capacity(data)
        
        # Output results
        if args.format == "json":
            output = format_json_output(result)
            print(json.dumps(output, indent=2))
        else:
            output = format_text_output(result)
            print(output)
        
        return 0
        
    except FileNotFoundError:
        print(f"Error: File '{args.data_file}' not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.data_file}': {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

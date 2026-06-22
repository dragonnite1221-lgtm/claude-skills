# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sprint_health_scorer_base import *  # noqa: F403,E402
# fmt: off
from sprint_health_scorer_p1 import HEALTH_DIMENSIONS  # noqa: E402,E501
from sprint_health_scorer_p2 import HealthScoreResult  # noqa: E402,E501
from sprint_health_scorer_p5 import analyze_sprint_health  # noqa: E402,E501
# fmt: on


def format_text_output(result: HealthScoreResult) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("="*60)
    lines.append("SPRINT HEALTH ANALYSIS REPORT")
    lines.append("="*60)
    lines.append("")
    
    if "error" in result.dimension_scores:
        lines.append(f"ERROR: {result.dimension_scores['error']}")
        return "\n".join(lines)
    
    # Overall health summary
    lines.append("OVERALL HEALTH SUMMARY")
    lines.append("-"*30)
    lines.append(f"Health Score: {result.overall_score:.1f}/100")
    lines.append(f"Health Grade: {result.health_grade.title()}")
    lines.append("")
    
    # Dimension scores
    lines.append("DIMENSION SCORES")
    lines.append("-"*30)
    
    for dimension, scores in result.dimension_scores.items():
        if isinstance(scores, dict) and "score" in scores:
            dimension_name = dimension.replace("_", " ").title()
            weight = HEALTH_DIMENSIONS[dimension]["weight"]
            lines.append(f"{dimension_name} (Weight: {weight:.0%})")
            lines.append(f"  Score: {scores['score']:.1f}/100 ({scores['grade'].title()})")
            lines.append(f"  Details: {scores['details']}")
            lines.append("")
    
    # Detailed metrics
    metrics = result.detailed_metrics
    if metrics:
        lines.append("DETAILED METRICS")
        lines.append("-"*30)
        lines.append(f"Sprints Analyzed: {metrics.get('sprint_count', 0)}")
        
        if "team_metrics" in metrics and metrics["team_metrics"]:
            team = metrics["team_metrics"]
            lines.append(f"Average Team Size: {team.get('average_team_size', 0):.1f}")
        
        if "story_metrics" in metrics and metrics["story_metrics"]:
            stories = metrics["story_metrics"]
            lines.append(f"Total Stories: {stories.get('total_stories', 0)}")
            lines.append(f"Completed Stories: {stories.get('completed_stories', 0)}")
            lines.append(f"Blocked Stories: {stories.get('blocked_stories', 0)}")
        
        if "blocker_metrics" in metrics and metrics["blocker_metrics"]:
            blockers = metrics["blocker_metrics"]
            lines.append(f"Total Blockers: {blockers.get('total_blockers', 0)}")
            lines.append(f"Average Resolution Time: {blockers.get('average_resolution_days', 0):.1f} days")
        
        lines.append("")
    
    # Recommendations
    if result.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-"*30)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
    
    return "\n".join(lines)
def format_json_output(result: HealthScoreResult) -> Dict[str, Any]:
    """Format results as JSON."""
    return {
        "overall_score": result.overall_score,
        "health_grade": result.health_grade,
        "dimension_scores": result.dimension_scores,
        "detailed_metrics": result.detailed_metrics,
        "recommendations": result.recommendations,
    }
def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze sprint health across multiple dimensions"
    )
    parser.add_argument(
        "data_file", 
        help="JSON file containing sprint health data"
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
        result = analyze_sprint_health(data)
        
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

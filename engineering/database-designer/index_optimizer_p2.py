# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(description="Optimize database indexes based on schema and query patterns")
    parser.add_argument("--schema", "-s", required=True, help="Schema definition JSON file")
    parser.add_argument("--queries", "-q", required=True, help="Query patterns JSON file")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text", 
                       help="Output format")
    parser.add_argument("--analyze-existing", "-e", action="store_true", 
                       help="Include analysis of existing indexes")
    parser.add_argument("--min-priority", "-p", type=int, default=4, 
                       help="Minimum priority level to include (1=highest, 4=lowest)")
    
    args = parser.parse_args()
    
    try:
        # Load schema
        with open(args.schema, 'r') as f:
            schema_data = json.load(f)
        
        # Load queries
        with open(args.queries, 'r') as f:
            query_data = json.load(f)
        
        # Initialize optimizer
        optimizer = IndexOptimizer()
        optimizer.load_schema(schema_data)
        optimizer.load_query_patterns(query_data)
        
        # Generate analysis
        analysis = optimizer.generate_analysis_report()
        
        # Filter by priority if specified
        if args.min_priority < 4:
            for priority_level in ["high_priority", "medium_priority", "low_priority"]:
                analysis["index_recommendations"][priority_level] = [
                    rec for rec in analysis["index_recommendations"][priority_level]
                    if rec["priority"] <= args.min_priority
                ]
        
        # Format output
        if args.format == "json":
            output = json.dumps(analysis, indent=2)
        else:
            output = optimizer.format_text_report(analysis)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

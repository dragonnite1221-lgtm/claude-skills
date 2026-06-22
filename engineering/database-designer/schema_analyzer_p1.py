# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(description="Analyze database schema for design issues and generate ERD")
    parser.add_argument("--input", "-i", required=True, help="Input file (SQL DDL or JSON schema)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--output-format", "-f", choices=["json", "text"], default="text",
                       help="Output format")
    parser.add_argument("--generate-erd", "-e", action="store_true", help="Include Mermaid ERD in output")
    parser.add_argument("--erd-only", action="store_true", help="Output only the Mermaid ERD")
    
    args = parser.parse_args()
    
    try:
        # Read input file
        with open(args.input, 'r') as f:
            content = f.read()
        
        # Initialize analyzer
        analyzer = SchemaAnalyzer()
        
        # Parse input based on file extension
        if args.input.lower().endswith('.json'):
            analyzer.parse_json_schema(content)
        else:
            analyzer.parse_sql_ddl(content)
        
        if not analyzer.tables:
            print("Error: No tables found in input file", file=sys.stderr)
            return 1
        
        if args.erd_only:
            # Output only ERD
            erd = analyzer.generate_mermaid_erd()
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(erd)
            else:
                print(erd)
            return 0
        
        # Perform analysis
        analyzer.analyze_normalization()
        analyzer.analyze_data_types()
        analyzer.analyze_constraints()
        analyzer.analyze_naming_conventions()
        
        # Generate report
        analysis = analyzer.get_analysis_summary()
        
        if args.generate_erd:
            analysis["mermaid_erd"] = analyzer.generate_mermaid_erd()
        
        # Output results
        if args.output_format == "json":
            output = json.dumps(analysis, indent=2)
        else:
            output = analyzer.format_text_report(analysis)
            if args.generate_erd:
                output += "\n\nMERMAID ERD\n" + "=" * 11 + "\n"
                output += analysis["mermaid_erd"]
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402


def format_human_readable_report(report: Dict[str, Any]) -> str:
    """Format the report in human-readable format."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("TECHNICAL DEBT SCAN REPORT")
    output.append("=" * 60)
    output.append(f"Directory: {report['scan_metadata']['directory']}")
    output.append(f"Scan Date: {report['scan_metadata']['scan_date']}")
    output.append(f"Scanner Version: {report['scan_metadata']['scanner_version']}")
    output.append("")
    
    # Summary
    summary = report["summary"]
    output.append("SUMMARY")
    output.append("-" * 30)
    output.append(f"Files Scanned: {summary['total_files_scanned']}")
    output.append(f"Lines Scanned: {summary['total_lines_scanned']:,}")
    output.append(f"Total Debt Items: {summary['total_debt_items']}")
    output.append(f"Health Score: {summary['health_score']}/100")
    output.append(f"Debt Density: {summary['debt_density']} items/file")
    output.append("")
    
    # Priority breakdown
    output.append("PRIORITY BREAKDOWN")
    output.append("-" * 30)
    for priority, count in summary["priority_breakdown"].items():
        output.append(f"{priority.capitalize()}: {count}")
    output.append("")
    
    # Top debt items
    output.append("TOP DEBT ITEMS")
    output.append("-" * 30)
    top_items = report["debt_items"][:10]
    for i, item in enumerate(top_items, 1):
        output.append(f"{i}. [{item['priority'].upper()}] {item['description']}")
        output.append(f"   File: {item['file_path']}")
        if 'line_number' in item:
            output.append(f"   Line: {item['line_number']}")
        output.append("")
    
    # Recommendations
    output.append("RECOMMENDATIONS")
    output.append("-" * 30)
    for i, rec in enumerate(report["recommendations"], 1):
        output.append(f"{i}. {rec}")
        output.append("")
    
    return "\n".join(output)


def main():
    """Main entry point for the debt scanner."""
    parser = argparse.ArgumentParser(description="Scan codebase for technical debt")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--config", help="Configuration file (JSON)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "text", "both"], 
                       default="both", help="Output format")
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    # Run scan
    scanner = DebtScanner(config)
    try:
        report = scanner.scan_directory(args.directory)
    except Exception as e:
        print(f"Scan failed: {e}")
        sys.exit(1)
    
    # Output results
    if args.format in ["json", "both"]:
        json_output = json.dumps(report, indent=2, default=str)
        if args.output:
            output_path = args.output if args.output.endswith('.json') else f"{args.output}.json"
            with open(output_path, 'w') as f:
                f.write(json_output)
            print(f"JSON report written to: {output_path}")
        else:
            print("\nJSON REPORT:")
            print("=" * 50)
            print(json_output)
    
    if args.format in ["text", "both"]:
        text_output = format_human_readable_report(report)
        if args.output:
            output_path = args.output if args.output.endswith('.txt') else f"{args.output}.txt"
            with open(output_path, 'w') as f:
                f.write(text_output)
            print(f"Text report written to: {output_path}")
        else:
            print("\nTEXT REPORT:")
            print("=" * 50)
            print(text_output)

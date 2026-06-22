# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Analyze and optimize alert configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze alert configuration
    python alert_optimizer.py --input alerts.json --analyze-only
    
    # Generate optimized configuration
    python alert_optimizer.py --input alerts.json --output optimized_alerts.json
    
    # Generate HTML report
    python alert_optimizer.py --input alerts.json --report report.html --format html
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Input alert configuration JSON file')
    parser.add_argument('--output', '-o',
                       help='Output optimized configuration JSON file')
    parser.add_argument('--report', '-r',
                       help='Generate analysis report file')
    parser.add_argument('--format', choices=['json', 'html'], default='json',
                       help='Report format (json or html)')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only perform analysis, do not generate optimized config')
    
    args = parser.parse_args()
    
    optimizer = AlertOptimizer()
    
    try:
        # Load alert configuration
        alert_config = optimizer.load_alert_config(args.input)
        
        # Perform analysis
        analysis_results = optimizer.analyze_configuration(alert_config)
        
        # Generate optimized configuration if requested
        if not args.analyze_only:
            optimized_config = optimizer.generate_optimized_config(
                alert_config.get('alerts', alert_config.get('rules', [])),
                analysis_results
            )
            
            output_file = args.output or 'optimized_alerts.json'
            optimizer.export_analysis(optimized_config, output_file, 'json')
            print(f"Optimized configuration saved to: {output_file}")
        
        # Generate report if requested
        if args.report:
            optimizer.export_analysis(analysis_results, args.report, args.format)
            print(f"Analysis report saved to: {args.report}")
        
        # Always show summary
        optimizer.print_summary(analysis_results)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

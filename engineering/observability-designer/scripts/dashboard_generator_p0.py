# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive dashboard specifications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate from service definition file
    python dashboard_generator.py --input service.json --output dashboard.json
    
    # Generate from command line parameters
    python dashboard_generator.py --service-type api --name "Payment Service" --output payment_dashboard.json
    
    # Generate Grafana-compatible JSON
    python dashboard_generator.py --input service.json --output dashboard.json --format grafana
    
    # Generate with specific role focus
    python dashboard_generator.py --service-type web --name "Frontend" --role developer --output frontend_dev.json
        """
    )
    
    parser.add_argument('--input', '-i',
                       help='Input service definition JSON file')
    parser.add_argument('--output', '-o', 
                       help='Output dashboard specification file')
    parser.add_argument('--service-type',
                       choices=['api', 'web', 'database', 'queue', 'batch', 'ml'],
                       help='Service type')
    parser.add_argument('--name',
                       help='Service name')
    parser.add_argument('--criticality',
                       choices=['critical', 'high', 'medium', 'low'],
                       default='medium',
                       help='Service criticality level')
    parser.add_argument('--role',
                       choices=['sre', 'developer', 'executive', 'ops'],
                       default='sre',
                       help='Target role for dashboard optimization')
    parser.add_argument('--format',
                       choices=['json', 'grafana'],
                       default='json',
                       help='Output format (json specification or grafana compatible)')
    parser.add_argument('--doc-output',
                       help='Generate documentation file')
    parser.add_argument('--summary-only', action='store_true',
                       help='Only display summary, do not save files')
    
    args = parser.parse_args()
    
    if not args.input and not (args.service_type and args.name):
        parser.error("Must provide either --input file or --service-type and --name")
    
    generator = DashboardGenerator()
    
    try:
        # Load or create service definition
        if args.input:
            service_def = generator.load_service_definition(args.input)
        else:
            service_def = generator.create_service_definition(
                args.service_type, args.name, args.criticality
            )
        
        # Generate dashboard specification
        dashboard_spec = generator.generate_dashboard_specification(service_def, args.role)
        
        # Output results
        if not args.summary_only:
            output_file = args.output or f"{service_def['name'].replace(' ', '_').lower()}_dashboard.json"
            generator.export_specification(dashboard_spec, output_file, args.format)
            print(f"Dashboard specification saved to: {output_file}")
            
            # Generate documentation if requested
            if args.doc_output:
                documentation = generator.generate_documentation(dashboard_spec)
                with open(args.doc_output, 'w') as f:
                    f.write(documentation)
                print(f"Documentation saved to: {args.doc_output}")
        
        # Always show summary
        generator.print_summary(dashboard_spec)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive SLO frameworks for services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate from service definition file
    python slo_designer.py --input service.json --output framework.json
    
    # Generate from command line parameters
    python slo_designer.py --service-type api --criticality high --user-facing true --output framework.json
    
    # Generate and display summary only
    python slo_designer.py --service-type web --criticality critical --user-facing true --summary-only
        """
    )
    
    parser.add_argument('--input', '-i', 
                       help='Input service definition JSON file')
    parser.add_argument('--output', '-o', 
                       help='Output framework JSON file')
    parser.add_argument('--service-type', 
                       choices=['api', 'web', 'database', 'queue', 'batch', 'ml'],
                       help='Service type')
    parser.add_argument('--criticality',
                       choices=['critical', 'high', 'medium', 'low'],
                       help='Service criticality level')
    parser.add_argument('--user-facing',
                       choices=['true', 'false'],
                       help='Whether service is user-facing')
    parser.add_argument('--service-name',
                       help='Service name')
    parser.add_argument('--summary-only', action='store_true',
                       help='Only display summary, do not save JSON')
    
    args = parser.parse_args()
    
    if not args.input and not (args.service_type and args.criticality and args.user_facing):
        parser.error("Must provide either --input file or --service-type, --criticality, and --user-facing")
    
    designer = SLODesigner()
    
    try:
        # Load or create service definition
        if args.input:
            service_def = designer.load_service_definition(args.input)
        else:
            user_facing = args.user_facing.lower() == 'true'
            service_def = designer.create_service_definition(
                args.service_type, args.criticality, user_facing, args.service_name
            )
        
        # Generate framework
        framework = designer.generate_framework(service_def)
        
        # Output results
        if not args.summary_only:
            output_file = args.output or f"{service_def['name']}_slo_framework.json"
            designer.export_json(framework, output_file)
            print(f"SLO framework saved to: {output_file}")
        
        # Always show summary
        designer.print_summary(framework)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402


def main():
    """Main entry point for the upgrade planner."""
    parser = argparse.ArgumentParser(
        description='Analyze dependency upgrades and create migration plans',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upgrade_planner.py deps.json
  python upgrade_planner.py inventory.json --timeline 60 --format json
  python upgrade_planner.py deps.json --risk-threshold medium --output plan.txt
        """
    )
    
    parser.add_argument('inventory_file',
                       help='Path to dependency inventory JSON file')
    parser.add_argument('--timeline', type=int, default=90,
                       help='Timeline for upgrade plan in days (default: 90)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: stdout)')
    parser.add_argument('--risk-threshold', 
                       choices=['safe', 'low', 'medium', 'high', 'critical'],
                       default='high',
                       help='Maximum risk level to include (default: high)')
    parser.add_argument('--security-only', action='store_true',
                       help='Only plan upgrades with security fixes')
    
    args = parser.parse_args()
    
    try:
        planner = UpgradePlanner()
        results = planner.analyze_upgrades(args.inventory_file, args.timeline)
        
        # Filter by risk threshold if specified
        if args.risk_threshold != 'critical':
            risk_levels = ['safe', 'low', 'medium', 'high', 'critical']
            max_index = risk_levels.index(args.risk_threshold)
            allowed_risks = set(risk_levels[:max_index + 1])
            
            results['available_upgrades'] = [
                u for u in results['available_upgrades']
                if u.risk_level.value in allowed_risks
            ]
        
        # Filter for security-only if specified
        if args.security_only:
            results['available_upgrades'] = [
                u for u in results['available_upgrades']
                if u.security_updates
            ]
        
        report = planner.generate_report(results, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Upgrade plan saved to {args.output}")
        else:
            print(report)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(
        description='GCP Cost Optimizer - Analyzes GCP resources and recommends cost savings'
    )
    parser.add_argument(
        '--resources', '-r',
        type=str,
        help='Path to JSON file with current GCP resource inventory'
    )
    parser.add_argument(
        '--monthly-spend', '-s',
        type=float,
        default=1000,
        help='Current monthly GCP spend in USD (default: 1000)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to write optimization report JSON'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON format'
    )
    parser.add_argument(
        '--checklist',
        action='store_true',
        help='Generate optimization checklist'
    )

    args = parser.parse_args()

    if args.resources:
        try:
            with open(args.resources, 'r') as f:
                resources = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{args.resources}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: File '{args.resources}' is not valid JSON.", file=sys.stderr)
            sys.exit(1)
    else:
        resources = {}

    optimizer = CostOptimizer(resources, args.monthly_spend)
    result = optimizer.analyze_and_optimize()

    if args.checklist:
        result['checklist'] = optimizer.generate_optimization_checklist()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Report written to {args.output}")
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nGCP Cost Optimization Report")
        print(f"{'=' * 40}")
        print(f"Current Monthly Spend: ${result['current_monthly_spend']:.2f}")
        print(f"Potential Savings:     ${result['potential_monthly_savings']:.2f}")
        print(f"Optimized Spend:       ${result['optimized_monthly_spend']:.2f}")
        print(f"Savings Percentage:    {result['savings_percentage']}%")
        print(f"\nTop Priority Actions:")
        for i, action in enumerate(result['priority_actions'], 1):
            print(f"  {i}. [{action['service']}] {action['recommendation']}")
            print(f"     Savings: ${action['potential_savings']:.2f}/month")
        print(f"\nTotal Recommendations: {len(result['recommendations'])}")

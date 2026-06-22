# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402
from okr_cascade_generator_p0 import parse_teams  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description='Generate OKR cascade from company strategy to team level',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate growth strategy OKRs with default teams
  python okr_cascade_generator.py growth

  # Custom teams
  python okr_cascade_generator.py retention --teams "Engineering,Design,Data,Growth"

  # Custom product contribution percentage
  python okr_cascade_generator.py revenue --contribution 0.4

  # JSON output
  python okr_cascade_generator.py innovation --json

  # All options combined
  python okr_cascade_generator.py operational --teams "Core,Platform" --contribution 0.5 --json
        """
    )

    parser.add_argument(
        'strategy',
        nargs='?',
        choices=['growth', 'retention', 'revenue', 'innovation', 'operational'],
        default='growth',
        help='Strategy type (default: growth)'
    )

    parser.add_argument(
        '--teams', '-t',
        type=str,
        help='Comma-separated list of team names (default: Growth,Platform,Mobile,Data)'
    )

    parser.add_argument(
        '--contribution', '-c',
        type=float,
        default=0.3,
        help='Product contribution to company OKRs as decimal (default: 0.3 = 30%%)'
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output as JSON instead of dashboard'
    )

    parser.add_argument(
        '--metrics', '-m',
        type=str,
        help='Metrics as JSON string (default: sample metrics)'
    )

    args = parser.parse_args()

    # Parse teams
    teams = parse_teams(args.teams)

    # Parse metrics
    if args.metrics:
        metrics = json.loads(args.metrics)
    else:
        metrics = {
            'current': 100000,
            'target': 150000,
            'current_revenue': 10,
            'target_revenue': 15,
            'current_nps': 40,
            'target_nps': 60
        }

    # Validate contribution
    if not 0 < args.contribution <= 1:
        print("Error: Contribution must be between 0 and 1")
        return 1

    # Generate OKRs
    generator = OKRGenerator(teams=teams, product_contribution=args.contribution)

    company_okrs = generator.generate_company_okrs(args.strategy, metrics)
    product_okrs = generator.cascade_to_product(company_okrs)
    team_okrs = generator.cascade_to_teams(product_okrs)

    all_okrs = {
        'quarter': company_okrs['quarter'],
        'strategy': args.strategy,
        'company': company_okrs,
        'product': product_okrs,
        'teams': team_okrs
    }

    alignment = generator.calculate_alignment_score(all_okrs)

    if args.json:
        all_okrs['alignment_scores'] = alignment
        all_okrs['config'] = {
            'teams': generator.teams,
            'product_contribution': generator.product_contribution
        }
        print(json.dumps(all_okrs, indent=2))
    else:
        dashboard = generator.generate_okr_dashboard(all_okrs)
        print(dashboard)

        print("\n\n🎯 ALIGNMENT SCORES")
        print("-" * 40)
        for metric, score in alignment.items():
            status = "✓" if score >= 80 else "!" if score >= 60 else "✗"
            print(f"{status} {metric.replace('_', ' ').title()}: {score}%")

        if alignment['overall'] >= 80:
            print("\n✅ Overall alignment is GOOD (≥80%)")
        elif alignment['overall'] >= 60:
            print("\n⚠️  Overall alignment NEEDS ATTENTION (60-80%)")
        else:
            print("\n❌ Overall alignment is POOR (<60%)")

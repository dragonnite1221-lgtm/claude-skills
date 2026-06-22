# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ApplicationType(Enum):
    """Types of applications supported."""
    WEB_APP = "web_application"
    MOBILE_BACKEND = "mobile_backend"
    DATA_PIPELINE = "data_pipeline"
    MICROSERVICES = "microservices"
    SAAS_PLATFORM = "saas_platform"
    ML_PLATFORM = "ml_platform"


def main():
    parser = argparse.ArgumentParser(
        description='GCP Architecture Designer - Recommends GCP services based on workload requirements'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Path to JSON file with application requirements'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to write design output JSON'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON format'
    )
    parser.add_argument(
        '--app-type',
        type=str,
        choices=['web_application', 'mobile_backend', 'data_pipeline',
                 'microservices', 'saas_platform', 'ml_platform'],
        default='web_application',
        help='Application type (default: web_application)'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=1000,
        help='Expected number of users (default: 1000)'
    )
    parser.add_argument(
        '--budget',
        type=float,
        default=500,
        help='Monthly budget in USD (default: 500)'
    )

    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, 'r') as f:
                requirements = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{args.input}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: File '{args.input}' is not valid JSON.", file=sys.stderr)
            sys.exit(1)
    else:
        requirements = {
            'application_type': args.app_type,
            'expected_users': args.users,
            'budget_monthly_usd': args.budget
        }

    designer = ArchitectureDesigner(requirements)
    result = designer.recommend_architecture_pattern()
    checklist = designer.generate_service_checklist()

    output = {
        'architecture': result,
        'implementation_checklist': checklist
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Design written to {args.output}")
    elif args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\nRecommended Pattern: {result['pattern_name']}")
        print(f"Description: {result['description']}")
        print(f"Use Case: {result['use_case']}")
        print(f"\nServices:")
        for name, svc in result['services'].items():
            print(f"  - {name}: {svc['service']} ({svc['purpose']})")
        print(f"\nEstimated Monthly Cost: ${result['estimated_cost']['monthly_usd']:.2f}")
        print(f"\nPros: {', '.join(result['pros'])}")
        print(f"Cons: {', '.join(result['cons'])}")

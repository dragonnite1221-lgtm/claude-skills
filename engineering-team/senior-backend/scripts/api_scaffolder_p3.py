# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Express.js routes from OpenAPI specification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s openapi.yaml --output src/routes/
  %(prog)s spec.json --framework fastify --output src/api/
  %(prog)s openapi.yaml --types-only --output src/types/
        '''
    )

    parser.add_argument(
        'spec',
        help='Path to OpenAPI specification (YAML or JSON)'
    )
    parser.add_argument(
        '--output', '-o',
        default='./generated',
        help='Output directory (default: ./generated)'
    )
    parser.add_argument(
        '--framework', '-f',
        choices=['express', 'fastify', 'koa'],
        default='express',
        help='Target framework (default: express)'
    )
    parser.add_argument(
        '--types-only',
        action='store_true',
        help='Generate only TypeScript types'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    try:
        scaffolder = APIScaffolder(
            spec_path=args.spec,
            output_dir=args.output,
            framework=args.framework,
            types_only=args.types_only,
            verbose=args.verbose,
        )

        results = scaffolder.run()

        print("-" * 50)
        print(f"Generated {results['routes_count']} route handlers")
        print(f"Generated {results['types_count']} type definitions")
        print(f"Output: {results['output']}")

        if args.json:
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

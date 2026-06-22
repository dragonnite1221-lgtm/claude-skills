# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from e2e_test_scaffolder_p6 import E2ETestScaffolder  # noqa: E402,E501
# fmt: on


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Playwright E2E tests from Next.js routes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scaffold E2E tests for App Router
  python e2e_test_scaffolder.py src/app/ --output e2e/

  # Include Page Object Models
  python e2e_test_scaffolder.py src/app/ --include-pom

  # Generate for specific routes only
  python e2e_test_scaffolder.py src/app/ --routes "/login,/dashboard,/checkout"

  # Verbose output
  python e2e_test_scaffolder.py pages/ -v
        """
    )
    parser.add_argument(
        'source',
        help='Source directory (app/ or pages/)'
    )
    parser.add_argument(
        '--output', '-o',
        default='e2e',
        help='Output directory for test files (default: e2e/)'
    )
    parser.add_argument(
        '--include-pom',
        action='store_true',
        help='Generate Page Object Model classes'
    )
    parser.add_argument(
        '--routes',
        help='Comma-separated list of routes to generate tests for'
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
        scaffolder = E2ETestScaffolder(
            source_path=args.source,
            output_path=args.output,
            include_pom=args.include_pom,
            routes=args.routes,
            verbose=args.verbose
        )

        results = scaffolder.run()

        if args.json:
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p2 import TestSuiteGenerator  # noqa: F401,E501


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Jest + React Testing Library test stubs for React components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan and generate tests
  python test_suite_generator.py src/components/ --output __tests__/

  # Scan only (don't generate)
  python test_suite_generator.py src/components/ --scan-only

  # Include accessibility tests
  python test_suite_generator.py src/ --include-a11y --output tests/

  # Verbose output
  python test_suite_generator.py src/components/ -v
        """
    )
    parser.add_argument(
        'source',
        help='Source directory containing React components'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for test files (default: <source>/__tests__/)'
    )
    parser.add_argument(
        '--include-a11y',
        action='store_true',
        help='Include accessibility tests using jest-axe'
    )
    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='Scan and report components without generating tests'
    )
    parser.add_argument(
        '--template',
        help='Custom template file for test generation'
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
        generator = TestSuiteGenerator(
            args.source,
            output_path=args.output,
            include_a11y=args.include_a11y,
            scan_only=args.scan_only,
            verbose=args.verbose,
            template=args.template
        )

        results = generator.run()

        if args.json:
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

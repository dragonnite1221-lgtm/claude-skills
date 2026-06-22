# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p9 import cmd_generate_suite, cmd_profile, cmd_validate  # noqa: F401,E501
from data_quality_validator_p10 import cmd_contract, cmd_schema  # noqa: F401,E501


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Data Quality Validator - Comprehensive data quality validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate data against schema
  python data_quality_validator.py validate data.csv --schema schema.json

  # Profile data
  python data_quality_validator.py profile data.csv --output profile.json

  # Generate Great Expectations suite
  python data_quality_validator.py generate-suite data.csv --output expectations.json

  # Validate against data contract
  python data_quality_validator.py contract data.csv --contract contract.yaml

  # Generate schema from data
  python data_quality_validator.py schema data.csv --output schema.json
        """
    )

    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data against schema')
    validate_parser.add_argument('input', help='Input data file (CSV, JSON, JSONL)')
    validate_parser.add_argument('--schema', '-s', help='Schema file (JSON)')
    validate_parser.add_argument('--output', '-o', help='Output report file')
    validate_parser.add_argument('--json', action='store_true', help='Output as JSON')
    validate_parser.add_argument('--detect-anomalies', action='store_true', help='Detect statistical anomalies')
    validate_parser.set_defaults(func=cmd_validate)

    # Profile command
    profile_parser = subparsers.add_parser('profile', help='Generate data profile')
    profile_parser.add_argument('input', help='Input data file')
    profile_parser.add_argument('--output', '-o', help='Output profile file')
    profile_parser.add_argument('--json', action='store_true', help='Output as JSON')
    profile_parser.set_defaults(func=cmd_profile)

    # Generate suite command
    suite_parser = subparsers.add_parser('generate-suite', help='Generate Great Expectations suite')
    suite_parser.add_argument('input', help='Input data file')
    suite_parser.add_argument('--output', '-o', help='Output expectations file')
    suite_parser.set_defaults(func=cmd_generate_suite)

    # Contract command
    contract_parser = subparsers.add_parser('contract', help='Validate against data contract')
    contract_parser.add_argument('input', help='Input data file')
    contract_parser.add_argument('--contract', '-c', required=True, help='Data contract file (YAML or JSON)')
    contract_parser.add_argument('--output', '-o', help='Output report file')
    contract_parser.add_argument('--json', action='store_true', help='Output as JSON')
    contract_parser.set_defaults(func=cmd_contract)

    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Generate schema from data')
    schema_parser.add_argument('input', help='Input data file')
    schema_parser.add_argument('--output', '-o', help='Output schema file')
    schema_parser.set_defaults(func=cmd_schema)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

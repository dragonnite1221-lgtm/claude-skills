# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p2 import PrefectGenerator  # noqa: F401,E501
from pipeline_orchestrator_p3 import DagsterGenerator  # noqa: F401,E501
from pipeline_orchestrator_p4 import pipeline_config_from_dict  # noqa: F401,E501
from pipeline_orchestrator_p5 import ETLPatternGenerator  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Orchestrator - Generate and manage data pipeline configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate Airflow DAG:
    python pipeline_orchestrator.py generate --type airflow --source postgres --destination snowflake --tables orders,customers

  Generate from config file:
    python pipeline_orchestrator.py generate --config pipeline.yaml --type prefect

  Validate existing DAG:
    python pipeline_orchestrator.py validate --dag dags/my_dag.py --type airflow
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate pipeline code')
    gen_parser.add_argument('--type', '-t', required=True,
                           choices=['airflow', 'prefect', 'dagster'],
                           help='Pipeline framework type')
    gen_parser.add_argument('--source', '-s', help='Source system type')
    gen_parser.add_argument('--destination', '-d', help='Destination system type')
    gen_parser.add_argument('--tables', help='Comma-separated list of tables')
    gen_parser.add_argument('--config', '-c', help='Configuration YAML file')
    gen_parser.add_argument('--output', '-o', help='Output file path')
    gen_parser.add_argument('--name', '-n', help='Pipeline name')
    gen_parser.add_argument('--schedule', default='0 5 * * *', help='Cron schedule')
    gen_parser.add_argument('--mode', default='incremental',
                           choices=['incremental', 'full'],
                           help='Load mode')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate pipeline code')
    val_parser.add_argument('--dag', required=True, help='DAG file to validate')
    val_parser.add_argument('--type', '-t', required=True,
                           choices=['airflow', 'prefect', 'dagster'])

    # Template command
    tmpl_parser = subparsers.add_parser('template', help='Generate from template')
    tmpl_parser.add_argument('--pattern', '-p', required=True,
                            choices=['extract-load', 'transform', 'cdc'],
                            help='ETL pattern to generate')
    tmpl_parser.add_argument('--type', '-t', required=True,
                            choices=['airflow', 'prefect', 'dagster'])
    tmpl_parser.add_argument('--source', '-s', required=True)
    tmpl_parser.add_argument('--destination', '-d', required=True)
    tmpl_parser.add_argument('--tables', required=True)
    tmpl_parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'generate':
            # Load config if provided
            if args.config:
                with open(args.config) as f:
                    if HAS_YAML:
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                config = pipeline_config_from_dict(config_data)
            else:
                # Build config from arguments
                tables = args.tables.split(',') if args.tables else []

                config = ETLPatternGenerator.generate_extract_load(
                    source_type=args.source or 'postgres',
                    destination_type=args.destination or 'snowflake',
                    tables=tables,
                    mode=args.mode
                )

                if args.name:
                    config.name = args.name
                config.schedule = args.schedule

            # Generate code
            generators = {
                'airflow': AirflowGenerator(),
                'prefect': PrefectGenerator(),
                'dagster': DagsterGenerator()
            }

            generator = generators[args.type]
            code = generator.generate(config)

            # Validate
            validation = generator.validate(code)
            if not validation['valid']:
                logger.warning(f"Validation issues: {validation['issues']}")

            # Output
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(code)
                logger.info(f"Generated pipeline saved to {args.output}")
            else:
                print(code)

        elif args.command == 'validate':
            with open(args.dag) as f:
                code = f.read()

            generators = {
                'airflow': AirflowGenerator(),
                'prefect': PrefectGenerator(),
                'dagster': DagsterGenerator()
            }

            generator = generators[args.type]
            result = generator.validate(code)

            print(json.dumps(result, indent=2))
            sys.exit(0 if result['valid'] else 1)

        elif args.command == 'template':
            tables = args.tables.split(',')

            if args.pattern == 'extract-load':
                config = ETLPatternGenerator.generate_extract_load(
                    source_type=args.source,
                    destination_type=args.destination,
                    tables=tables
                )
            elif args.pattern == 'transform':
                config = ETLPatternGenerator.generate_transform_pipeline(
                    source_tables=tables,
                    target_table='fct_output',
                    dbt_models=['stg_*', 'fct_*']
                )
            else:
                logger.error(f"Pattern {args.pattern} not yet implemented")
                sys.exit(1)

            generators = {
                'airflow': AirflowGenerator(),
                'prefect': PrefectGenerator(),
                'dagster': DagsterGenerator()
            }

            generator = generators[args.type]
            code = generator.generate(config)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(code)
                logger.info(f"Generated {args.pattern} pipeline saved to {args.output}")
            else:
                print(code)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

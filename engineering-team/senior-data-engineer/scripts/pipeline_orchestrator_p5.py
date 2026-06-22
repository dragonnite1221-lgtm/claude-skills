# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import DestinationConfig, PipelineConfig, SourceConfig, TaskConfig, sql_string_literal, validate_dbt_selector, validate_freshness_cutoff, validate_sql_identifier  # noqa: F401,E501


class ETLPatternGenerator:
    """Generate common ETL patterns."""

    @staticmethod
    def generate_extract_load(
        source_type: str,
        destination_type: str,
        tables: List[str],
        mode: str = "incremental"
    ) -> PipelineConfig:
        """Generate extract-load pipeline configuration."""
        if mode not in {"incremental", "full"}:
            raise ValueError(f"Unsupported extract mode: {mode}")

        tasks = []

        # Extract tasks
        for table in tables:
            table_name = validate_sql_identifier(table, "table")
            extract_task = TaskConfig(
                task_id=f"extract_{table_name.replace('.', '_')}",
                operator="python_operator",
                params={
                    'callable': f"extract_{table_name.replace('.', '_')}",
                    'sql': f'SELECT * FROM {table_name}' + (
                        f" WHERE updated_at > {AIRFLOW_PREV_DS_SQL}"
                        if mode == 'incremental' else ''
                    )
                }
            )
            tasks.append(extract_task)

        # Load tasks with dependencies
        for table in tables:
            table_name = validate_sql_identifier(table, "table")
            task_suffix = table_name.replace(".", "_")
            load_task = TaskConfig(
                task_id=f"load_{task_suffix}",
                operator="python_operator",
                dependencies=[f"extract_{task_suffix}"],
                params={'callable': f"load_{task_suffix}"}
            )
            tasks.append(load_task)

        # Quality check task
        quality_task = TaskConfig(
            task_id="quality_check",
            operator="python_operator",
            dependencies=[f"load_{table}" for table in tables],
            params={'callable': 'run_quality_checks'}
        )
        tasks.append(quality_task)

        return PipelineConfig(
            name=f"el_{source_type}_to_{destination_type}",
            description=f"Extract from {source_type}, load to {destination_type}",
            schedule="0 5 * * *",  # Daily at 5 AM
            tags=["etl", source_type, destination_type],
            source=SourceConfig(
                type=source_type,
                connection_id=f"{source_type}_default",
                tables=tables,
                incremental_strategy="timestamp" if mode == "incremental" else "full"
            ),
            destination=DestinationConfig(
                type=destination_type,
                connection_id=f"{destination_type}_default",
                write_mode="append" if mode == "incremental" else "overwrite"
            ),
            tasks=tasks
        )

    @staticmethod
    def generate_transform_pipeline(
        source_tables: List[str],
        target_table: str,
        dbt_models: List[str],
        freshness_column: str = "updated_at",
        freshness_cutoff_expr: str = "{{ ds }}",
    ) -> PipelineConfig:
        """Generate transformation pipeline with dbt."""

        tasks = []
        validate_sql_identifier(target_table, "target table")
        freshness_column = validate_sql_identifier(freshness_column, "freshness column")

        # Sensor for source freshness
        for table in source_tables:
            table_name = validate_sql_identifier(table, "table")
            sensor_task = TaskConfig(
                task_id=f"wait_for_{table_name.replace('.', '_')}",
                operator="sql_sensor",
                params={
                    'sql': (
                        f"SELECT MAX({freshness_column}) FROM {table_name} "
                        f"WHERE {freshness_column} > "
                        f"{sql_string_literal(validate_freshness_cutoff(freshness_cutoff_expr))}"
                    )
                }
            )
            tasks.append(sensor_task)

        # dbt run task
        dbt_run = TaskConfig(
            task_id="dbt_run",
            operator="bash_operator",
            dependencies=[
                f"wait_for_{validate_sql_identifier(t, 'table').replace('.', '_')}"
                for t in source_tables
            ],
            params={
                'command': (
                    "cd /opt/dbt && dbt run --select "
                    + " ".join(validate_dbt_selector(model) for model in dbt_models)
                )
            },
            timeout_minutes=120
        )
        tasks.append(dbt_run)

        # dbt test task
        dbt_test = TaskConfig(
            task_id="dbt_test",
            operator="bash_operator",
            dependencies=["dbt_run"],
            params={
                'command': f'cd /opt/dbt && dbt test --select {" ".join(dbt_models)}'
            }
        )
        tasks.append(dbt_test)

        return PipelineConfig(
            name=f"transform_{target_table}",
            description=f"Transform data into {target_table} using dbt",
            schedule="0 6 * * *",  # Daily at 6 AM (after extraction)
            tags=["transform", "dbt"],
            tasks=tasks
        )

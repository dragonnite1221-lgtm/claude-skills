"""Regression tests for the senior-data-engineer pipeline orchestrator."""

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR = (
    REPO_ROOT
    / "engineering-team"
    / "senior-data-engineer"
    / "scripts"
    / "pipeline_orchestrator.py"
)


def load_orchestrator_module():
    spec = importlib.util.spec_from_file_location("pipeline_orchestrator", ORCHESTRATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_airflow_sql_operator_import_is_generated():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="daily_sql",
        description="Daily SQL pipeline",
        schedule="@daily",
        source=module.SourceConfig(type="postgres", connection_id="warehouse"),
        tasks=[
            module.TaskConfig(
                task_id="wait_for_rows",
                operator="sql_sensor",
                params={"sql": "SELECT 1"},
            )
        ],
    )

    code = module.AirflowGenerator().generate(config)

    assert "from airflow.providers.postgres.operators.postgres import PostgresOperator" in code
    assert "wait_for_rows = PostgresOperator(" in code


def test_airflow_generic_sql_uses_common_sql_operator_without_postgres_source():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="daily_sql",
        description="Daily SQL pipeline",
        schedule="@daily",
        tasks=[
            module.TaskConfig(
                task_id="run_statement",
                operator="sql",
                params={"sql": "SELECT 1", "conn_id": "warehouse"},
            )
        ],
    )

    code = module.AirflowGenerator().generate(config)

    assert "from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator" in code
    assert "run_statement = SQLExecuteQueryOperator(" in code
    assert "conn_id='warehouse'" in code
    assert "PostgresOperator" not in code


def test_airflow_generic_sql_rejects_multi_statement_sql():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="daily_sql",
        description="Daily SQL pipeline",
        schedule="@daily",
        tasks=[
            module.TaskConfig(
                task_id="run_statement",
                operator="sql",
                params={"sql": "SELECT 1; DROP TABLE users"},
            )
        ],
    )

    with pytest.raises(ValueError, match="single statement"):
        module.AirflowGenerator().generate(config)


def test_airflow_python_task_rejects_unsafe_callable_name():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="python_task",
        description="Python task",
        schedule="@daily",
        tasks=[
            module.TaskConfig(
                task_id="run_python",
                operator="python",
                params={"callable": "process); evil("},
            )
        ],
    )

    with pytest.raises(ValueError, match="Invalid Python callable"):
        module.AirflowGenerator().generate(config)


def test_airflow_snowflake_operator_import_is_generated_from_operator_name():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="load_snowflake",
        description="Load Snowflake from S3",
        schedule="@daily",
        destination=module.DestinationConfig(type="snowflake", connection_id="warehouse"),
        tasks=[
            module.TaskConfig(
                task_id="load_table",
                operator="s3_to_snowflake",
                params={"sql": "SELECT 1"},
            )
        ],
    )

    code = module.AirflowGenerator().generate(config)

    assert (
        "from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator"
        in code
    )
    assert "load_table = SnowflakeOperator(" in code
    assert "snowflake_conn_id='warehouse'" in code


def test_airflow_generic_task_imports_python_operator():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="generic_task",
        description="Generic task",
        schedule="@daily",
        tasks=[module.TaskConfig(task_id="custom_step", operator="custom")],
    )

    code = module.AirflowGenerator().generate(config)

    assert "from airflow.operators.python import PythonOperator" in code
    assert "custom_step = PythonOperator(" in code


def test_pipeline_config_from_dict_builds_nested_dataclasses():
    module = load_orchestrator_module()
    config = module.pipeline_config_from_dict(
        {
            "name": "daily_load",
            "description": "Daily load",
            "schedule": "@daily",
            "source": {"type": "postgres", "connection_id": "source_db"},
            "destination": {"type": "snowflake", "connection_id": "warehouse"},
            "tasks": [
                {
                    "task_id": "extract",
                    "operator": "python",
                    "params": {"callable": "extract_data"},
                }
            ],
        }
    )

    assert isinstance(config.source, module.SourceConfig)
    assert isinstance(config.destination, module.DestinationConfig)
    assert isinstance(config.tasks[0], module.TaskConfig)


def test_prefect_generator_preserves_multiple_dependencies():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="multi_dep",
        description="Multiple dependencies",
        schedule="@daily",
        tasks=[
            module.TaskConfig(task_id="extract_a", operator="python"),
            module.TaskConfig(task_id="extract_b", operator="python"),
            module.TaskConfig(
                task_id="combine",
                operator="python",
                dependencies=["extract_a", "extract_b"],
            ),
        ],
    )

    code = module.PrefectGenerator().generate(config)

    assert "result_2 = combine([result_0, result_1])" in code


def test_dagster_generator_preserves_multiple_dependencies():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="multi_dep",
        description="Multiple dependencies",
        schedule="@daily",
        tasks=[
            module.TaskConfig(task_id="extract_a", operator="python"),
            module.TaskConfig(task_id="extract_b", operator="python"),
            module.TaskConfig(
                task_id="combine",
                operator="python",
                dependencies=["extract_a", "extract_b"],
            ),
        ],
    )

    code = module.DagsterGenerator().generate(config)

    assert 'ins={"extract_a": In(), "extract_b": In()}' in code
    assert "def combine(context, extract_a, extract_b):" in code
    assert "combine_output = combine(extract_a_output, extract_b_output)" in code


def test_dagster_generator_orders_dependencies_before_dependents():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="out_of_order",
        description="Out of order dependencies",
        schedule="@daily",
        tasks=[
            module.TaskConfig(
                task_id="combine",
                operator="python",
                dependencies=["extract"],
            ),
            module.TaskConfig(task_id="extract", operator="python"),
        ],
    )

    code = module.DagsterGenerator().generate(config)

    assert code.index("extract_output = extract()") < code.index(
        "combine_output = combine(extract_output)"
    )


def test_missing_dependency_is_rejected_before_code_generation():
    module = load_orchestrator_module()
    config = module.PipelineConfig(
        name="missing_dep",
        description="Missing dependency",
        schedule="@daily",
        tasks=[
            module.TaskConfig(
                task_id="combine",
                operator="python",
                dependencies=["extract"],
            ),
        ],
    )

    with pytest.raises(ValueError, match="unknown task extract"):
        module.PrefectGenerator().generate(config)


def test_transform_pipeline_freshness_query_is_configurable():
    module = load_orchestrator_module()

    config = module.ETLPatternGenerator.generate_transform_pipeline(
        ["orders"],
        "mart_orders",
        ["orders_model"],
        freshness_column="loaded_at",
        freshness_cutoff_expr="{{ data_interval_start }}",
    )

    assert config.tasks[0].params["sql"] == (
        "SELECT MAX(loaded_at) FROM orders WHERE loaded_at > '{{ data_interval_start }}'"
    )


def test_transform_pipeline_rejects_unsafe_freshness_expression():
    module = load_orchestrator_module()

    with pytest.raises(ValueError, match="Invalid freshness cutoff"):
        module.ETLPatternGenerator.generate_transform_pipeline(
            ["orders"],
            "mart_orders",
            ["orders_model"],
            freshness_cutoff_expr="{{ ds }}; DROP TABLE orders",
        )

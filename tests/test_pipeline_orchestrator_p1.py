# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_pipeline_orchestrator_base import *  # noqa: F403,E402


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

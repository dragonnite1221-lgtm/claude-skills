#!/usr/bin/env python3
"""
Pipeline Orchestrator

Generate pipeline configurations for Airflow, Prefect, and Dagster.
Supports ETL pattern generation, dependency management, and scheduling.

Usage:
    python pipeline_orchestrator.py generate --type airflow --source postgres --destination snowflake
    python pipeline_orchestrator.py generate --type prefect --config pipeline.yaml
    python pipeline_orchestrator.py visualize --dag dags/my_dag.py
    python pipeline_orchestrator.py validate --dag dags/my_dag.py
"""

import os
import sys
import json
import re
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
import logging
import argparse
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PYTHON_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
AIRFLOW_MACRO_RE = re.compile(r"^\{\{\s*[A-Za-z_][A-Za-z0-9_.]*\s*\}\}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DBT_SELECTOR_RE = re.compile(r"^[A-Za-z0-9_./:+,@-]+$")
AIRFLOW_PREV_DS_SQL = "'{{ prev_ds }}'"


def python_string_literal(value: Any) -> str:
    """Return a generated-code-safe Python string literal."""
    return repr(str(value))


def validate_sql_identifier(value: str, label: str = "identifier") -> str:
    """Validate simple SQL identifiers used by template generators."""
    parts = value.split(".")
    if not parts or not all(SQL_IDENTIFIER_RE.match(part) for part in parts):
        raise ValueError(f"Invalid SQL {label}: {value}")
    return value


def validate_python_identifier(value: str, label: str = "identifier") -> str:
    """Validate Python identifiers emitted into generated code."""
    if not PYTHON_IDENTIFIER_RE.match(value):
        raise ValueError(f"Invalid Python {label}: {value}")
    return value


def sql_string_literal(value: str) -> str:
    """Return an escaped SQL string literal for already-validated scalar values."""
    return "'" + value.replace("'", "''") + "'"


def validate_sql_statement(value: Any) -> str:
    """Validate read-only SQL statements accepted by generic task configs."""
    sql = str(value).strip()
    lowered = sql.lower()
    if "\x00" in sql or ";" in sql or "--" in sql or "/*" in sql or "*/" in sql:
        raise ValueError("SQL statements must be a single statement without comments")
    if not (lowered.startswith("select ") or lowered.startswith("with ")):
        raise ValueError("SQL statements must start with SELECT or WITH")
    return sql


def validate_freshness_cutoff(value: str) -> str:
    """Validate freshness cutoff values before embedding them as SQL literals."""
    if AIRFLOW_MACRO_RE.match(value) or ISO_DATE_RE.match(value):
        return value
    raise ValueError(f"Invalid freshness cutoff: {value}")


def validate_dbt_selector(value: str) -> str:
    """Validate dbt selector fragments used by template generators."""
    if not DBT_SELECTOR_RE.match(value):
        raise ValueError(f"Invalid dbt selector: {value}")
    return value


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SourceConfig:
    """Source system configuration."""
    type: str  # postgres, mysql, s3, kafka, api
    connection_id: str
    schema: Optional[str] = None
    tables: List[str] = field(default_factory=list)
    query: Optional[str] = None
    incremental_column: Optional[str] = None
    incremental_strategy: str = "timestamp"  # timestamp, id, cdc

@dataclass
class DestinationConfig:
    """Destination system configuration."""
    type: str  # snowflake, bigquery, redshift, s3, delta
    connection_id: str
    schema: str = "raw"
    write_mode: str = "append"  # append, overwrite, merge
    partition_by: Optional[str] = None
    cluster_by: List[str] = field(default_factory=list)

@dataclass
class TaskConfig:
    """Individual task configuration."""
    task_id: str
    operator: str
    dependencies: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    retries: int = 2
    retry_delay_minutes: int = 5
    timeout_minutes: int = 60
    pool: Optional[str] = None
    priority_weight: int = 1

@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    name: str
    description: str
    schedule: str  # cron expression or @daily, @hourly
    owner: str = "data-team"
    tags: List[str] = field(default_factory=list)
    catchup: bool = False
    max_active_runs: int = 1
    default_retries: int = 2
    source: Optional[SourceConfig] = None
    destination: Optional[DestinationConfig] = None
    tasks: List[TaskConfig] = field(default_factory=list)


# ============================================================================
# Pipeline Generators
# ============================================================================

class PipelineGenerator(ABC):
    """Abstract base class for pipeline generators."""

    @abstractmethod
    def generate(self, config: PipelineConfig) -> str:
        """Generate pipeline code from config."""
        pass

    @abstractmethod
    def validate(self, code: str) -> Dict[str, Any]:
        """Validate generated pipeline code."""
        pass


def order_tasks_by_dependencies(tasks: List[TaskConfig]) -> List[TaskConfig]:
    """Return tasks in dependency order while preserving original order where possible."""
    tasks_by_id = {task.task_id: task for task in tasks}
    ordered = []
    visiting = set()
    visited = set()

    def visit(task: TaskConfig):
        if task.task_id in visited:
            return
        if task.task_id in visiting:
            raise ValueError(f"Cycle detected in task dependencies at {task.task_id}")

        visiting.add(task.task_id)
        for dependency in task.dependencies:
            dependency_task = tasks_by_id.get(dependency)
            if dependency_task is None:
                raise ValueError(f"Task {task.task_id} depends on unknown task {dependency}")
            visit(dependency_task)
        visiting.remove(task.task_id)
        visited.add(task.task_id)
        ordered.append(task)

    for task in tasks:
        visit(task)

    return ordered


class AirflowGenerator(PipelineGenerator):
    """Generate Airflow DAG code."""

    OPERATOR_IMPORTS = {
        'python': 'from airflow.operators.python import PythonOperator',
        'bash': 'from airflow.operators.bash import BashOperator',
        'sql': 'from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator',
        'postgres': 'from airflow.providers.postgres.operators.postgres import PostgresOperator',
        'snowflake': 'from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator',
        's3': 'from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator',
        's3_to_snowflake': 'from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator',
        'sensor': 'from airflow.sensors.base import BaseSensorOperator',
        'trigger': 'from airflow.operators.trigger_dagrun import TriggerDagRunOperator',
        'email': 'from airflow.operators.email import EmailOperator',
        'slack': 'from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator',
    }

    def generate(self, config: PipelineConfig) -> str:
        """Generate Airflow DAG from configuration."""

        # Collect required imports
        imports = self._collect_imports(config)

        # Generate DAG code
        code = self._generate_header(imports)
        code += self._generate_default_args(config)
        code += self._generate_dag_definition(config)
        code += self._generate_tasks(config)
        code += self._generate_dependencies(config)

        return code

    def _collect_imports(self, config: PipelineConfig) -> List[str]:
        """Collect required import statements."""
        imports = [
            "from airflow import DAG",
            "from airflow.utils.dates import days_ago",
            "from datetime import datetime, timedelta",
        ]

        operators_used = set()
        for task in config.tasks:
            operator = task.operator.lower()
            if 'python' in operator:
                operators_used.add('python')
            elif 'bash' in operator:
                operators_used.add('bash')
            elif 'postgres' in operator:
                operators_used.add('postgres')
            elif 'sql' in operator:
                if config.source and config.source.type == 'postgres':
                    operators_used.add('postgres')
                else:
                    operators_used.add('sql')
            elif 'snowflake' in operator:
                operators_used.add('snowflake')
            else:
                operators_used.add('python')

        # Add source/destination specific imports
        if config.source:
            if config.source.type == 'postgres':
                operators_used.add('postgres')
            elif config.source.type == 's3':
                operators_used.add('s3')

        if config.destination:
            if config.destination.type == 'snowflake':
                operators_used.add('snowflake')
                operators_used.add('s3_to_snowflake')

        for op in operators_used:
            if op in self.OPERATOR_IMPORTS:
                imports.append(self.OPERATOR_IMPORTS[op])

        return imports

    def _generate_header(self, imports: List[str]) -> str:
        """Generate file header with imports."""
        header = '''"""
Auto-generated Airflow DAG
Generated by Pipeline Orchestrator
"""

'''
        header += '\n'.join(imports)
        header += '\n\n'
        return header

    def _generate_default_args(self, config: PipelineConfig) -> str:
        """Generate default_args dictionary."""
        return f'''
default_args = {{
    'owner': '{config.owner}',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': {config.default_retries},
    'retry_delay': timedelta(minutes=5),
}}

'''

    def _generate_dag_definition(self, config: PipelineConfig) -> str:
        """Generate DAG definition."""
        tags_str = str(config.tags) if config.tags else "[]"

        return f'''
with DAG(
    dag_id='{config.name}',
    default_args=default_args,
    description='{config.description}',
    schedule_interval='{config.schedule}',
    start_date=days_ago(1),
    catchup={config.catchup},
    max_active_runs={config.max_active_runs},
    tags={tags_str},
) as dag:

'''

    def _generate_tasks(self, config: PipelineConfig) -> str:
        """Generate task definitions."""
        tasks_code = ""

        for task in config.tasks:
            if 'python' in task.operator.lower():
                tasks_code += self._generate_python_task(task)
            elif 'bash' in task.operator.lower():
                tasks_code += self._generate_bash_task(task)
            elif 'snowflake' in task.operator.lower():
                tasks_code += self._generate_snowflake_task(task, config)
            elif 'sql' in task.operator.lower() or 'postgres' in task.operator.lower():
                tasks_code += self._generate_sql_task(task, config)
            else:
                tasks_code += self._generate_generic_task(task)

        return tasks_code

    def _generate_python_task(self, task: TaskConfig) -> str:
        """Generate PythonOperator task."""
        callable_name = validate_python_identifier(
            str(task.params.get('callable', 'process_data')),
            "callable",
        )
        return f'''
    def {callable_name}(**kwargs):
        """Task: {task.task_id}"""
        # Add your processing logic here
        execution_date = kwargs.get('ds')
        print(f"Processing data for {{execution_date}}")
        return True

    {task.task_id} = PythonOperator(
        task_id='{task.task_id}',
        python_callable={callable_name},
        retries={task.retries},
        retry_delay=timedelta(minutes={task.retry_delay_minutes}),
        execution_timeout=timedelta(minutes={task.timeout_minutes}),
    )

'''

    def _generate_bash_task(self, task: TaskConfig) -> str:
        """Generate BashOperator task."""
        command = python_string_literal(task.params.get('command', 'echo "Hello World"'))
        return f'''
    {task.task_id} = BashOperator(
        task_id='{task.task_id}',
        bash_command={command},
        retries={task.retries},
        retry_delay=timedelta(minutes={task.retry_delay_minutes}),
        execution_timeout=timedelta(minutes={task.timeout_minutes}),
    )

'''

    def _generate_sql_task(self, task: TaskConfig, config: PipelineConfig) -> str:
        """Generate SQL operator task."""
        sql = python_string_literal(validate_sql_statement(task.params.get('sql', 'SELECT 1')))
        conn_id = python_string_literal(task.params.get(
            'conn_id',
            config.source.connection_id if config.source else 'default_conn',
        ))
        provider = task.params.get('provider', config.source.type if config.source else 'common_sql')

        if provider == 'postgres' or 'postgres' in task.operator.lower():
            return f'''
    {task.task_id} = PostgresOperator(
        task_id='{task.task_id}',
        postgres_conn_id={conn_id},
        sql={sql},
        retries={task.retries},
        retry_delay=timedelta(minutes={task.retry_delay_minutes}),
    )

'''

        return f'''
    {task.task_id} = SQLExecuteQueryOperator(
        task_id='{task.task_id}',
        conn_id={conn_id},
        sql={sql},
        retries={task.retries},
        retry_delay=timedelta(minutes={task.retry_delay_minutes}),
    )

'''

    def _generate_snowflake_task(self, task: TaskConfig, config: PipelineConfig) -> str:
        """Generate SnowflakeOperator task."""
        sql = python_string_literal(validate_sql_statement(task.params.get('sql', 'SELECT 1')))
        conn_id = python_string_literal(task.params.get(
            'conn_id',
            config.destination.connection_id
            if config.destination and config.destination.type == 'snowflake'
            else 'snowflake_default',
        ))
        return f'''
    {task.task_id} = SnowflakeOperator(
        task_id='{task.task_id}',
        snowflake_conn_id={conn_id},
        sql={sql},
        retries={task.retries},
        retry_delay=timedelta(minutes={task.retry_delay_minutes}),
    )

'''

    def _generate_generic_task(self, task: TaskConfig) -> str:
        """Generate generic task placeholder."""
        return f'''
    # TODO: Implement {task.operator} for {task.task_id}
    {task.task_id} = PythonOperator(
        task_id='{task.task_id}',
        python_callable=lambda: print("{task.task_id}"),
    )

'''

    def _generate_dependencies(self, config: PipelineConfig) -> str:
        """Generate task dependencies."""
        deps_code = "\n    # Task dependencies\n"

        for task in config.tasks:
            if task.dependencies:
                for dep in task.dependencies:
                    deps_code += f"    {dep} >> {task.task_id}\n"

        return deps_code

    def validate(self, code: str) -> Dict[str, Any]:
        """Validate generated DAG code."""
        issues = []
        warnings = []

        # Check for common issues
        if 'default_args' not in code:
            issues.append("Missing default_args definition")

        if 'with DAG' not in code:
            issues.append("Missing DAG context manager")

        if 'schedule_interval' not in code and 'schedule=' not in code:
            warnings.append("No schedule_interval defined, DAG won't run automatically")

        # Try to parse the code
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }


class PrefectGenerator(PipelineGenerator):
    """Generate Prefect flow code."""

    def generate(self, config: PipelineConfig) -> str:
        """Generate Prefect flow from configuration."""

        code = self._generate_header()
        code += self._generate_tasks(config)
        code += self._generate_flow(config)

        return code

    def _generate_header(self) -> str:
        """Generate file header."""
        return '''"""
Auto-generated Prefect Flow
Generated by Pipeline Orchestrator
"""

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta

'''

    def _generate_tasks(self, config: PipelineConfig) -> str:
        """Generate Prefect tasks."""
        tasks_code = ""

        for task_config in config.tasks:
            cache_expiration = task_config.params.get('cache_hours', 1)
            tasks_code += f'''
@task(
    name="{task_config.task_id}",
    retries={task_config.retries},
    retry_delay_seconds={task_config.retry_delay_minutes * 60},
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours={cache_expiration}),
)
def {task_config.task_id}(input_data=None):
    """Task: {task_config.task_id}"""
    logger = get_run_logger()
    logger.info(f"Executing {task_config.task_id}")

    # Add processing logic here
    result = input_data

    return result

'''
        return tasks_code

    def _generate_flow(self, config: PipelineConfig) -> str:
        """Generate Prefect flow."""
        flow_code = f'''
@flow(
    name="{config.name}",
    description="{config.description}",
    version="1.0.0",
)
def {config.name.replace('-', '_')}_flow():
    """Main flow orchestrating all tasks."""
    logger = get_run_logger()
    logger.info("Starting flow: {config.name}")

'''
        # Generate task calls with dependencies
        task_vars = {}
        for i, task_config in enumerate(order_tasks_by_dependencies(config.tasks)):
            task_name = task_config.task_id
            var_name = f"result_{i}"
            task_vars[task_name] = var_name

            if task_config.dependencies:
                dep_vars = [task_vars.get(dep, "None") for dep in task_config.dependencies]
                input_expr = dep_vars[0] if len(dep_vars) == 1 else f"[{', '.join(dep_vars)}]"
                flow_code += f"    {var_name} = {task_name}({input_expr})\n"
            else:
                flow_code += f"    {var_name} = {task_name}()\n"

        flow_code += '''
    logger.info("Flow completed successfully")
    return True


if __name__ == "__main__":
    ''' + f'{config.name.replace("-", "_")}_flow()' + '\n'

        return flow_code

    def validate(self, code: str) -> Dict[str, Any]:
        """Validate Prefect flow code."""
        issues = []

        if '@flow' not in code:
            issues.append("Missing @flow decorator")

        if '@task' not in code:
            issues.append("No tasks defined with @task decorator")

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': []
        }


class DagsterGenerator(PipelineGenerator):
    """Generate Dagster job code."""

    def generate(self, config: PipelineConfig) -> str:
        """Generate Dagster job from configuration."""

        code = self._generate_header()
        code += self._generate_ops(config)
        code += self._generate_job(config)

        return code

    def _generate_header(self) -> str:
        """Generate file header."""
        return '''"""
Auto-generated Dagster Job
Generated by Pipeline Orchestrator
"""

from dagster import op, job, In, Out, Output, DynamicOut, graph
from dagster import AssetMaterialization, MetadataValue

'''

    def _generate_ops(self, config: PipelineConfig) -> str:
        """Generate Dagster ops."""
        ops_code = ""

        for task_config in config.tasks:
            has_input = len(task_config.dependencies) > 0

            if has_input:
                ins = ", ".join(f'"{dep}": In()' for dep in task_config.dependencies)
                args = ", ".join(task_config.dependencies)
                if len(task_config.dependencies) == 1:
                    result_expr = task_config.dependencies[0]
                else:
                    result_items = ", ".join(f'"{dep}": {dep}' for dep in task_config.dependencies)
                    result_expr = f"{{{result_items}}}"
                ops_code += f'''
@op(
    ins={{{ins}}},
    out=Out(),
)
def {task_config.task_id}(context, {args}):
    """Op: {task_config.task_id}"""
    context.log.info(f"Executing {task_config.task_id}")

    # Add processing logic here
    result = {result_expr}

    # Log asset materialization
    yield AssetMaterialization(
        asset_key="{task_config.task_id}",
        metadata={{
            "row_count": MetadataValue.int(len(result) if hasattr(result, '__len__') else 0),
        }}
    )
    yield Output(result)

'''
            else:
                ops_code += f'''
@op(out=Out())
def {task_config.task_id}(context):
    """Op: {task_config.task_id}"""
    context.log.info(f"Executing {task_config.task_id}")

    # Add processing logic here
    result = {{}}

    yield AssetMaterialization(
        asset_key="{task_config.task_id}",
    )
    yield Output(result)

'''
        return ops_code

    def _generate_job(self, config: PipelineConfig) -> str:
        """Generate Dagster job."""
        job_code = f'''
@job(
    name="{config.name}",
    description="{config.description}",
    tags={{
        "owner": "{config.owner}",
        "schedule": "{config.schedule}",
    }},
)
def {config.name.replace('-', '_')}_job():
    """Main job orchestrating all ops."""
'''
        # Build dependency graph
        task_outputs = {}
        for task_config in order_tasks_by_dependencies(config.tasks):
            task_name = task_config.task_id

            if task_config.dependencies:
                dep_outputs = [task_outputs.get(dep, "None") for dep in task_config.dependencies]
                job_code += f"    {task_name}_output = {task_name}({', '.join(dep_outputs)})\n"
            else:
                job_code += f"    {task_name}_output = {task_name}()\n"

            task_outputs[task_name] = f"{task_name}_output"

        return job_code

    def validate(self, code: str) -> Dict[str, Any]:
        """Validate Dagster job code."""
        issues = []

        if '@job' not in code:
            issues.append("Missing @job decorator")

        if '@op' not in code:
            issues.append("No ops defined with @op decorator")

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': []
        }


def pipeline_config_from_dict(config_data: Dict[str, Any]) -> PipelineConfig:
    """Build PipelineConfig and nested dataclasses from parsed JSON/YAML data."""
    data = dict(config_data)

    if isinstance(data.get('source'), dict):
        data['source'] = SourceConfig(**data['source'])

    if isinstance(data.get('destination'), dict):
        data['destination'] = DestinationConfig(**data['destination'])

    tasks = data.get('tasks')
    if isinstance(tasks, list):
        data['tasks'] = [
            TaskConfig(**task) if isinstance(task, dict) else task
            for task in tasks
        ]

    return PipelineConfig(**data)


# ============================================================================
# ETL Pattern Templates
# ============================================================================

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


# ============================================================================
# CLI Interface
# ============================================================================

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


if __name__ == '__main__':
    main()

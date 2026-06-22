# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import PipelineConfig, TaskConfig, python_string_literal, validate_python_identifier, validate_sql_statement  # noqa: F401,E501


class AirflowGeneratorMixin1:
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

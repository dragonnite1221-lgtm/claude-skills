# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import PipelineConfig, TaskConfig  # noqa: F401,E501


class AirflowGeneratorMixin2:
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

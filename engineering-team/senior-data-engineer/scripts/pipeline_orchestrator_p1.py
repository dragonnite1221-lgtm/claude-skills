# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import TaskConfig  # noqa: F401,E501


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

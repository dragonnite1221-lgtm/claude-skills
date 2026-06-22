# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import DestinationConfig, PipelineConfig, SourceConfig, TaskConfig  # noqa: F401,E501


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

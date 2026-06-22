# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_orchestrator_base import *  # noqa: F403,E402
from pipeline_orchestrator_p0 import DestinationConfig, PipelineConfig, PipelineGenerator, SourceConfig, TaskConfig, python_string_literal, sql_string_literal, validate_dbt_selector, validate_freshness_cutoff, validate_python_identifier, validate_sql_identifier, validate_sql_statement  # noqa: F401,E501
from pipeline_orchestrator_p1 import order_tasks_by_dependencies  # noqa: F401,E501
from pipeline_orchestrator_p2 import PrefectGenerator  # noqa: F401,E501
from pipeline_orchestrator_p3 import DagsterGenerator  # noqa: F401,E501
from pipeline_orchestrator_p4 import pipeline_config_from_dict  # noqa: F401,E501
from pipeline_orchestrator_p5 import ETLPatternGenerator  # noqa: F401,E501
from pipeline_orchestrator_p6 import main  # noqa: F401,E501
from pipeline_orchestrator_c0 import AirflowGeneratorMixin0  # noqa: F401
from pipeline_orchestrator_c1 import AirflowGeneratorMixin1  # noqa: F401
from pipeline_orchestrator_c2 import AirflowGeneratorMixin2  # noqa: F401


class AirflowGenerator(AirflowGeneratorMixin0, AirflowGeneratorMixin1, AirflowGeneratorMixin2, PipelineGenerator):
    pass


if __name__ == '__main__':
    main()

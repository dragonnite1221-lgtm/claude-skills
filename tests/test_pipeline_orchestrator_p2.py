# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_pipeline_orchestrator_base import *  # noqa: F403,E402
# fmt: off
from test_pipeline_orchestrator_p1 import load_orchestrator_module  # noqa: E402,E501
# fmt: on


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

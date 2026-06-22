# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p1 import ProcessData  # noqa: E402,E501
from ops_efficiency_analyzer_p2 import _generate_toc_recommendation  # noqa: E402,E501
# fmt: on


def analyze_bottlenecks(processes: list[ProcessData]) -> dict[str, Any]:
    """
    Identify bottlenecks using throughput analysis.
    Bottleneck = step with lowest throughput (or highest queue buildup).
    """
    bottlenecks = []
    throughput_chain = []

    for process in processes:
        steps = process.get("steps", [])
        if not steps:
            continue

        step_analysis = []
        min_throughput = float("inf")
        bottleneck_step = None

        for step in steps:
            throughput = step.get("throughput_per_day", 0)
            queue_depth = step.get("current_queue", 0)
            avg_wait_hours = step.get("avg_wait_hours", 0)

            # Utilization estimate
            capacity = step.get("capacity_per_day", throughput * 1.2)
            utilization = (throughput / capacity * 100) if capacity > 0 else 100

            step_info = {
                "name": step["name"],
                "throughput_per_day": throughput,
                "queue_depth": queue_depth,
                "avg_wait_hours": avg_wait_hours,
                "utilization_pct": round(utilization, 1),
                "is_bottleneck": False,
            }
            step_analysis.append(step_info)

            if throughput < min_throughput:
                min_throughput = throughput
                bottleneck_step = step_info

        if bottleneck_step:
            bottleneck_step["is_bottleneck"] = True

            # Calculate flow efficiency
            total_lead_time = sum(
                s.get("avg_wait_hours", 0) + s.get("avg_process_hours", 1)
                for s in steps
            )
            total_process_time = sum(s.get("avg_process_hours", 1) for s in steps)
            flow_efficiency = (
                (total_process_time / total_lead_time * 100)
                if total_lead_time > 0
                else 0
            )

            bottlenecks.append({
                "process": process["name"],
                "bottleneck_step": bottleneck_step["name"],
                "bottleneck_throughput": min_throughput,
                "bottleneck_queue": bottleneck_step["queue_depth"],
                "flow_efficiency_pct": round(flow_efficiency, 1),
                "steps": step_analysis,
                "toc_recommendation": _generate_toc_recommendation(
                    bottleneck_step, process
                ),
            })

        throughput_chain.append({
            "process": process["name"],
            "steps": step_analysis,
        })

    # Rank bottlenecks by severity (queue depth × utilization)
    for b in bottlenecks:
        b["severity_score"] = b["bottleneck_queue"] * (b["bottleneck_throughput"] or 1)
    bottlenecks.sort(key=lambda x: x["severity_score"], reverse=True)

    return {
        "bottlenecks": bottlenecks,
        "throughput_chain": throughput_chain,
    }
def _expected_layers(headcount: int) -> int:
    if headcount <= 15:
        return 1
    elif headcount <= 50:
        return 2
    elif headcount <= 150:
        return 3
    elif headcount <= 500:
        return 4
    else:
        return 5
def _dept_revenue_benchmark(dept_name: str, stage: str) -> int:
    """Revenue per employee benchmark by department and stage (USD)."""
    benchmarks = {
        "series_a": {
            "engineering": 400000,
            "sales": 250000,
            "customer_success": 300000,
            "marketing": 500000,
            "operations": 400000,
            "product": 400000,
            "default": 200000,
        },
        "series_b": {
            "engineering": 500000,
            "sales": 350000,
            "customer_success": 400000,
            "marketing": 700000,
            "operations": 500000,
            "product": 500000,
            "default": 300000,
        },
        "series_c": {
            "engineering": 600000,
            "sales": 450000,
            "customer_success": 500000,
            "marketing": 900000,
            "operations": 600000,
            "product": 600000,
            "default": 400000,
        },
    }
    stage_data = benchmarks.get(stage, benchmarks["series_a"])
    dept_key = dept_name.lower().replace(" ", "_").replace("-", "_")
    return stage_data.get(dept_key, stage_data["default"])

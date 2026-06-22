# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402
# fmt: off
from ops_efficiency_analyzer_p1 import MATURITY_CRITERIA, MATURITY_LEVELS, ProcessData, _get_improvement_action  # noqa: E402,E501
# fmt: on


def score_process_maturity(process: ProcessData) -> dict[str, Any]:
    """
    Score a single process on 1-5 maturity scale.
    Returns scored process with dimension breakdown and recommendations.
    """
    maturity_inputs = process.get("maturity", {})
    total_score = 0.0
    dimension_scores = {}
    recommendations = []

    for dimension, config in MATURITY_CRITERIA.items():
        raw_score = maturity_inputs.get(dimension, 0)
        # Normalize raw score (0-5) to weight
        normalized = (raw_score / 5.0) * config["weight"] * 5
        total_score += normalized
        dimension_scores[dimension] = raw_score

        # Generate recommendation if below threshold
        if raw_score < 3:
            severity = "🔴 Critical" if raw_score < 2 else "🟡 Needs work"
            recommendations.append({
                "dimension": dimension,
                "current_score": raw_score,
                "target_score": 3,
                "severity": severity,
                "action": _get_improvement_action(dimension, raw_score),
            })

    # Clamp to 1-5 range (scores can't be below 1 for a running process)
    maturity_score = max(1.0, min(5.0, total_score))
    maturity_level = round(maturity_score)

    return {
        "name": process["name"],
        "maturity_score": round(maturity_score, 2),
        "maturity_level": maturity_level,
        "maturity_label": MATURITY_LEVELS[maturity_level],
        "dimension_scores": dimension_scores,
        "recommendations": recommendations,
        "process_data": process,
    }
def _generate_toc_recommendation(bottleneck_step: dict, process: ProcessData) -> str:
    """Generate a Theory of Constraints recommendation for a bottleneck."""
    util = bottleneck_step["utilization_pct"]
    queue = bottleneck_step["queue_depth"]
    step_name = bottleneck_step["name"]

    if util >= 90:
        return (
            f"ELEVATE: '{step_name}' is at {util}% utilization — at capacity. "
            f"Add resources (people, automation, or parallel processing) immediately. "
            f"Queue of {queue} units will grow until capacity is increased."
        )
    elif util >= 70:
        return (
            f"EXPLOIT: '{step_name}' has capacity headroom but is the constraint. "
            f"Eliminate non-value-add work in this step. Protect it from interruptions. "
            f"Ensure upstream steps feed it steadily, not in batches."
        )
    else:
        return (
            f"INVESTIGATE: '{step_name}' shows low throughput ({bottleneck_step['throughput_per_day']}/day) "
            f"despite available capacity. Root cause may be upstream blocking, "
            f"unclear handoffs, or quality issues requiring rework."
        )

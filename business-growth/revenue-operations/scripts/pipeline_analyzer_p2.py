# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pipeline_analyzer_p1 import safe_divide  # noqa: E402,E501
# fmt: on


def analyze_deal_aging(
    deals: list[dict], average_cycle_days: int, stages: list[str]
) -> dict[str, Any]:
    """Analyze deal aging and flag stale deals.

    Flags deals older than 2x the average cycle time.
    Uses stage-specific thresholds based on position in the pipeline.
    """
    aging_threshold = average_cycle_days * 2
    num_stages = len(stages)
    stage_order = {stage: i for i, stage in enumerate(stages)}

    # Stage-specific thresholds: early stages get more time, later stages less
    stage_thresholds: dict[str, int] = {}
    for i, stage in enumerate(stages):
        if stage == "Closed Won":
            continue
        # Progressive thresholds: first stage gets full cycle, last open stage gets 50%
        progress = safe_divide(i, num_stages - 1)
        threshold = int(average_cycle_days * (1.0 + (1.0 - progress)))
        stage_thresholds[stage] = threshold

    aging_deals = []
    healthy_deals = 0
    at_risk_deals = 0

    for deal in deals:
        if deal["stage"] == "Closed Won":
            continue

        stage = deal["stage"]
        age = deal["age_days"]
        threshold = stage_thresholds.get(stage, aging_threshold)

        if age > threshold:
            at_risk_deals += 1
            aging_deals.append({
                "id": deal["id"],
                "name": deal["name"],
                "stage": stage,
                "age_days": age,
                "threshold_days": threshold,
                "days_over": age - threshold,
                "value": deal["value"],
            })
        else:
            healthy_deals += 1

    aging_deals.sort(key=lambda x: x["days_over"], reverse=True)

    return {
        "global_aging_threshold_days": aging_threshold,
        "stage_thresholds": stage_thresholds,
        "total_open_deals": healthy_deals + at_risk_deals,
        "healthy_deals": healthy_deals,
        "at_risk_deals": at_risk_deals,
        "aging_deals": aging_deals,
    }

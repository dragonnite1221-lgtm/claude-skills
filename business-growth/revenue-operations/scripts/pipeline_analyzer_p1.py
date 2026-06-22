# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pipeline_analyzer_base import *  # noqa: F403,E402


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()
def get_quarter(d: date) -> str:
    """Return the quarter string for a given date (e.g., '2025-Q1')."""
    quarter = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{quarter}"
def calculate_coverage_ratio(deals: list[dict], quota: float) -> dict[str, Any]:
    """Calculate pipeline coverage ratio against quota.

    Target: 3-4x pipeline coverage for healthy pipeline.
    """
    total_pipeline = sum(d["value"] for d in deals if d["stage"] != "Closed Won")
    ratio = safe_divide(total_pipeline, quota)

    if ratio >= 4.0:
        rating = "Strong"
    elif ratio >= 3.0:
        rating = "Healthy"
    elif ratio >= 2.0:
        rating = "At Risk"
    else:
        rating = "Critical"

    return {
        "total_pipeline_value": total_pipeline,
        "quota": quota,
        "coverage_ratio": round(ratio, 2),
        "rating": rating,
        "target": "3.0x - 4.0x",
    }
def calculate_stage_conversion_rates(
    deals: list[dict], stages: list[str]
) -> list[dict[str, Any]]:
    """Calculate stage-to-stage conversion rates.

    Measures the percentage of deals that progress from one stage to the next.
    """
    stage_order = {stage: i for i, stage in enumerate(stages)}
    stage_counts: dict[str, int] = {stage: 0 for stage in stages}

    for deal in deals:
        stage = deal["stage"]
        if stage in stage_order:
            stage_idx = stage_order[stage]
            # A deal at stage N has passed through all stages 0..N
            for i in range(stage_idx + 1):
                stage_counts[stages[i]] += 1

    conversions = []
    for i in range(len(stages) - 1):
        from_stage = stages[i]
        to_stage = stages[i + 1]
        from_count = stage_counts[from_stage]
        to_count = stage_counts[to_stage]
        rate = safe_divide(to_count, from_count) * 100

        conversions.append({
            "from_stage": from_stage,
            "to_stage": to_stage,
            "from_count": from_count,
            "to_count": to_count,
            "conversion_rate_pct": round(rate, 1),
        })

    return conversions
def calculate_sales_velocity(deals: list[dict]) -> dict[str, Any]:
    """Calculate sales velocity.

    Formula: (# opportunities x avg deal size x win rate) / avg sales cycle length
    Result is revenue per day.
    """
    if not deals:
        return {
            "num_opportunities": 0,
            "avg_deal_size": 0,
            "win_rate_pct": 0,
            "avg_cycle_days": 0,
            "velocity_per_day": 0,
            "velocity_per_month": 0,
        }

    won_deals = [d for d in deals if d["stage"] == "Closed Won"]
    open_deals = [d for d in deals if d["stage"] != "Closed Won"]
    all_considered = deals

    num_opportunities = len(all_considered)
    avg_deal_size = safe_divide(
        sum(d["value"] for d in all_considered), num_opportunities
    )
    win_rate = safe_divide(len(won_deals), num_opportunities)
    avg_cycle_days = safe_divide(
        sum(d["age_days"] for d in all_considered), num_opportunities
    )

    velocity_per_day = safe_divide(
        num_opportunities * avg_deal_size * win_rate, avg_cycle_days
    )

    return {
        "num_opportunities": num_opportunities,
        "avg_deal_size": round(avg_deal_size, 2),
        "win_rate_pct": round(win_rate * 100, 1),
        "avg_cycle_days": round(avg_cycle_days, 1),
        "velocity_per_day": round(velocity_per_day, 2),
        "velocity_per_month": round(velocity_per_day * 30, 2),
    }

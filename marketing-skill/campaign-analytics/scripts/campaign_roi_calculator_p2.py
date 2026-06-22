# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from campaign_roi_calculator_base import *  # noqa: F403,E402
# fmt: off
from campaign_roi_calculator_p1 import assess_performance, get_benchmark, safe_divide  # noqa: E402,E501
# fmt: on


def calculate_campaign_metrics(campaign: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate all ROI metrics for a single campaign.

    Args:
        campaign: Dict with keys: name, channel, spend, revenue, impressions, clicks, leads, customers.

    Returns:
        Dict with all calculated metrics, benchmarks, and assessments.
    """
    name = campaign.get("name", "Unnamed Campaign")
    channel = campaign.get("channel", "default")
    spend = campaign.get("spend", 0.0)
    revenue = campaign.get("revenue", 0.0)
    impressions = campaign.get("impressions", 0)
    clicks = campaign.get("clicks", 0)
    leads = campaign.get("leads", 0)
    customers = campaign.get("customers", 0)

    # Core metrics
    roi = safe_divide(revenue - spend, spend) * 100
    roas = safe_divide(revenue, spend)
    cpa = safe_divide(spend, customers) if customers > 0 else None
    cpl = safe_divide(spend, leads) if leads > 0 else None
    cac = safe_divide(spend, customers) if customers > 0 else None
    ctr = safe_divide(clicks, impressions) * 100 if impressions > 0 else None
    cvr = safe_divide(customers, leads) * 100 if leads > 0 else None
    cpc = safe_divide(spend, clicks) if clicks > 0 else None
    cpm = safe_divide(spend, impressions) * 1000 if impressions > 0 else None
    lead_conversion_rate = safe_divide(leads, clicks) * 100 if clicks > 0 else None

    # Profit
    profit = revenue - spend

    # Benchmark assessments
    assessments: Dict[str, Any] = {}
    flags: List[str] = []

    if ctr is not None:
        benchmark = get_benchmark("ctr", channel)
        assessment = assess_performance(ctr, benchmark, higher_is_better=True)
        assessments["ctr"] = {
            "value": round(ctr, 2),
            "benchmark_range": {"low": benchmark[0], "target": benchmark[1], "high": benchmark[2]},
            "assessment": assessment,
        }
        if assessment == "underperforming":
            flags.append(f"CTR ({ctr:.2f}%) is below industry low ({benchmark[0]}%) for {channel}")

    if roas > 0:
        benchmark = get_benchmark("roas", channel)
        assessment = assess_performance(roas, benchmark, higher_is_better=True)
        assessments["roas"] = {
            "value": round(roas, 2),
            "benchmark_range": {"low": benchmark[0], "target": benchmark[1], "high": benchmark[2]},
            "assessment": assessment,
        }
        if assessment == "underperforming":
            flags.append(f"ROAS ({roas:.2f}x) is below industry low ({benchmark[0]}x) for {channel}")

    if cpa is not None:
        benchmark = get_benchmark("cpa", channel)
        assessment = assess_performance(cpa, benchmark, higher_is_better=False)
        assessments["cpa"] = {
            "value": round(cpa, 2),
            "benchmark_range": {"low": benchmark[0], "target": benchmark[1], "high": benchmark[2]},
            "assessment": assessment,
        }
        if assessment == "underperforming":
            flags.append(f"CPA (${cpa:.2f}) exceeds industry high (${benchmark[2]:.2f}) for {channel}")

    if profit < 0:
        flags.append(f"Campaign is unprofitable: ${profit:,.2f} net loss")

    # Recommendations
    recommendations: List[str] = []
    if ctr is not None and assessments.get("ctr", {}).get("assessment") in ("below_target", "underperforming"):
        recommendations.append("Improve ad creative and targeting to increase CTR")
    if assessments.get("roas", {}).get("assessment") in ("below_target", "underperforming"):
        recommendations.append("Review targeting and bid strategy to improve ROAS")
    if assessments.get("cpa", {}).get("assessment") in ("below_target", "underperforming"):
        recommendations.append("Optimize landing pages and conversion flow to reduce CPA")
    if cvr is not None and cvr < 10:
        recommendations.append("Lead-to-customer conversion is low; review sales process and lead quality")
    if lead_conversion_rate is not None and lead_conversion_rate < 2:
        recommendations.append("Click-to-lead rate is low; improve landing page relevance and form experience")
    if profit > 0 and assessments.get("roas", {}).get("assessment") in ("good", "excellent"):
        recommendations.append("Campaign performing well; consider scaling budget")

    return {
        "name": name,
        "channel": channel,
        "metrics": {
            "spend": round(spend, 2),
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
            "roi_pct": round(roi, 2),
            "roas": round(roas, 2),
            "cpa": round(cpa, 2) if cpa is not None else None,
            "cpl": round(cpl, 2) if cpl is not None else None,
            "cac": round(cac, 2) if cac is not None else None,
            "ctr_pct": round(ctr, 2) if ctr is not None else None,
            "cvr_pct": round(cvr, 2) if cvr is not None else None,
            "cpc": round(cpc, 2) if cpc is not None else None,
            "cpm": round(cpm, 2) if cpm is not None else None,
            "lead_conversion_rate_pct": round(lead_conversion_rate, 2) if lead_conversion_rate is not None else None,
            "impressions": impressions,
            "clicks": clicks,
            "leads": leads,
            "customers": customers,
        },
        "assessments": assessments,
        "flags": flags,
        "recommendations": recommendations,
    }

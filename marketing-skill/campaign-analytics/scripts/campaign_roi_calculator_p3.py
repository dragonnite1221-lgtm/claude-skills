# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from campaign_roi_calculator_base import *  # noqa: F403,E402
# fmt: off
from campaign_roi_calculator_p1 import safe_divide  # noqa: E402,E501
# fmt: on


def calculate_portfolio_summary(campaign_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate metrics across all campaigns.

    Args:
        campaign_results: List of individual campaign result dicts.

    Returns:
        Portfolio-level summary with totals and weighted averages.
    """
    total_spend = sum(c["metrics"]["spend"] for c in campaign_results)
    total_revenue = sum(c["metrics"]["revenue"] for c in campaign_results)
    total_impressions = sum(c["metrics"]["impressions"] for c in campaign_results)
    total_clicks = sum(c["metrics"]["clicks"] for c in campaign_results)
    total_leads = sum(c["metrics"]["leads"] for c in campaign_results)
    total_customers = sum(c["metrics"]["customers"] for c in campaign_results)
    total_profit = total_revenue - total_spend

    underperforming = [c["name"] for c in campaign_results if c["flags"]]
    top_performers = sorted(
        campaign_results,
        key=lambda c: c["metrics"]["roi_pct"],
        reverse=True,
    )

    # Channel breakdown
    channel_totals: Dict[str, Dict[str, float]] = {}
    for c in campaign_results:
        ch = c["channel"]
        if ch not in channel_totals:
            channel_totals[ch] = {"spend": 0, "revenue": 0, "leads": 0, "customers": 0}
        channel_totals[ch]["spend"] += c["metrics"]["spend"]
        channel_totals[ch]["revenue"] += c["metrics"]["revenue"]
        channel_totals[ch]["leads"] += c["metrics"]["leads"]
        channel_totals[ch]["customers"] += c["metrics"]["customers"]

    channel_summary = {}
    for ch, totals in channel_totals.items():
        channel_summary[ch] = {
            "spend": round(totals["spend"], 2),
            "revenue": round(totals["revenue"], 2),
            "roi_pct": round(safe_divide(totals["revenue"] - totals["spend"], totals["spend"]) * 100, 2),
            "roas": round(safe_divide(totals["revenue"], totals["spend"]), 2),
            "leads": int(totals["leads"]),
            "customers": int(totals["customers"]),
        }

    return {
        "total_campaigns": len(campaign_results),
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "portfolio_roi_pct": round(safe_divide(total_profit, total_spend) * 100, 2),
        "portfolio_roas": round(safe_divide(total_revenue, total_spend), 2),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_leads": total_leads,
        "total_customers": total_customers,
        "blended_ctr_pct": round(safe_divide(total_clicks, total_impressions) * 100, 2),
        "blended_cpl": round(safe_divide(total_spend, total_leads), 2) if total_leads > 0 else None,
        "blended_cpa": round(safe_divide(total_spend, total_customers), 2) if total_customers > 0 else None,
        "underperforming_campaigns": underperforming,
        "top_performer": top_performers[0]["name"] if top_performers else None,
        "channel_summary": channel_summary,
    }

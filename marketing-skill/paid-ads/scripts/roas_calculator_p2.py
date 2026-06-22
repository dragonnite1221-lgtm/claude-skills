# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from roas_calculator_base import *  # noqa: F403,E402
# fmt: off
from roas_calculator_p1 import _recommendations, _roas_label  # noqa: E402,E501
# fmt: on


def calculate(spend: float, revenue: float = 0.0, conversions: int = 0,
              leads: int = 0, margin_pct: float = 0.0,
              impressions: int = 0, clicks: int = 0) -> dict:

    results = {
        "inputs": {
            "ad_spend": spend,
            "revenue": revenue,
            "conversions": conversions,
            "leads": leads,
            "margin_pct": margin_pct,
            "impressions": impressions,
            "clicks": clicks,
        }
    }

    metrics = {}

    # --- ROAS ---
    if revenue > 0 and spend > 0:
        roas = revenue / spend
        metrics["roas"] = {
            "value": round(roas, 2),
            "formula": "revenue / ad_spend",
            "interpretation": _roas_label(roas),
        }

    # --- Break-even ROAS ---
    if margin_pct > 0:
        be_roas = 100 / margin_pct
        metrics["break_even_roas"] = {
            "value": round(be_roas, 2),
            "formula": "100 / margin_%",
            "note": f"Need {be_roas:.1f}x ROAS to cover ad costs at {margin_pct}% margin",
        }
        if revenue > 0:
            actual_roas = revenue / spend
            profitable = actual_roas >= be_roas
            metrics["profitability"] = {
                "is_profitable": profitable,
                "gap": round(actual_roas - be_roas, 2),
                "note": "Profitable ✅" if profitable else f"Unprofitable ❌ — need +{be_roas - actual_roas:.2f}x ROAS",
            }

    # --- CPA ---
    if conversions > 0 and spend > 0:
        cpa = spend / conversions
        metrics["cpa"] = {
            "value": round(cpa, 2),
            "formula": "ad_spend / conversions",
            "unit": "cost per acquisition",
        }
        if revenue > 0:
            rev_per_conversion = revenue / conversions
            metrics["revenue_per_conversion"] = {
                "value": round(rev_per_conversion, 2),
                "roi_per_conversion": round((rev_per_conversion - cpa) / cpa * 100, 1),
            }

    # --- CPL ---
    if leads > 0 and spend > 0:
        cpl = spend / leads
        metrics["cpl"] = {
            "value": round(cpl, 2),
            "formula": "ad_spend / leads",
            "unit": "cost per lead",
        }
        if conversions > 0:
            lead_to_conv_rate = conversions / leads * 100
            metrics["lead_to_conversion_rate"] = {
                "value": round(lead_to_conv_rate, 1),
                "unit": "%",
            }

    # --- Conversion rate ---
    if clicks > 0 and conversions > 0:
        cvr = conversions / clicks * 100
        metrics["conversion_rate"] = {
            "value": round(cvr, 2),
            "unit": "%",
            "benchmark": "2-5% typical for paid search",
        }
    if clicks > 0 and leads > 0:
        lcr = leads / clicks * 100
        metrics["lead_capture_rate"] = {
            "value": round(lcr, 2),
            "unit": "%",
        }

    # --- CTR ---
    if impressions > 0 and clicks > 0:
        ctr = clicks / impressions * 100
        metrics["ctr"] = {
            "value": round(ctr, 2),
            "unit": "%",
            "benchmark": "2-5% for search, 0.1-0.5% for display",
        }
        cpm = spend / impressions * 1000
        metrics["cpm"] = {
            "value": round(cpm, 2),
            "unit": "cost per 1000 impressions",
        }
        cpc = spend / clicks
        metrics["cpc"] = {
            "value": round(cpc, 2),
            "unit": "cost per click",
        }

    results["metrics"] = metrics
    results["recommendations"] = _recommendations(metrics, spend, margin_pct)
    return results
DEMO_DATA = {
    "spend": 8500,
    "revenue": 34200,
    "conversions": 142,
    "leads": 680,
    "margin_pct": 35,
    "impressions": 185000,
    "clicks": 3700,
}

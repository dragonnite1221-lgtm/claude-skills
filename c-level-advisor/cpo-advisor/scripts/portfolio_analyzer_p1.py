# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from portfolio_analyzer_base import *  # noqa: F403,E402


def sample_data() -> dict:
    """
    Sample portfolio. Replace with real product data.

    Fields:
      name              Product name
      revenue_quarterly Current quarter revenue (any consistent currency)
      revenue_prev_q    Revenue last quarter (for QoQ calculation)
      market_growth_pct Annual market growth rate (percent, e.g. 12.5 for 12.5%)
      your_market_share Your estimated market share (percent, e.g. 8.0 for 8%)
      largest_competitor_share  Largest competitor's share (percent)
      eng_capacity_pct  % of total engineering capacity allocated (0-100)
      d30_retention     Optional D30 retention rate (decimal, e.g. 0.45)
      nps               Optional NPS score (-100 to 100)
      notes             Optional free text notes for the report
    """
    return {
        "company": "Acme Corp",
        "total_engineering_headcount": 45,
        "products": [
            {
                "name": "CorePlatform",
                "revenue_quarterly": 480000,
                "revenue_prev_q": 430000,
                "market_growth_pct": 22.0,
                "your_market_share": 18.0,
                "largest_competitor_share": 12.0,
                "eng_capacity_pct": 35,
                "d30_retention": 0.61,
                "nps": 52,
                "notes": "Our flagship. Leading market share in fast-growing segment.",
            },
            {
                "name": "ReportingModule",
                "revenue_quarterly": 290000,
                "revenue_prev_q": 285000,
                "market_growth_pct": 5.0,
                "your_market_share": 22.0,
                "largest_competitor_share": 18.0,
                "eng_capacity_pct": 25,
                "d30_retention": 0.58,
                "nps": 38,
                "notes": "Mature product, strong margins, slow market.",
            },
            {
                "name": "MobileApp",
                "revenue_quarterly": 95000,
                "revenue_prev_q": 78000,
                "market_growth_pct": 35.0,
                "your_market_share": 3.5,
                "largest_competitor_share": 24.0,
                "eng_capacity_pct": 28,
                "d30_retention": 0.31,
                "nps": 22,
                "notes": "High growth market. We're far behind on share. Bet or exit.",
            },
            {
                "name": "LegacyConnector",
                "revenue_quarterly": 62000,
                "revenue_prev_q": 68000,
                "market_growth_pct": -3.0,
                "your_market_share": 8.0,
                "largest_competitor_share": 35.0,
                "eng_capacity_pct": 12,
                "d30_retention": 0.42,
                "nps": 14,
                "notes": "Declining market. Customers are on long-term contracts.",
            },
        ],
    }
GROWTH_THRESHOLD_PCT = 10.0
SHARE_RATIO_THRESHOLD = 1.0
def bcg_quadrant(market_growth_pct: float, share_ratio: float) -> str:
    high_growth = market_growth_pct >= GROWTH_THRESHOLD_PCT
    leading_share = share_ratio >= SHARE_RATIO_THRESHOLD

    if high_growth and leading_share:
        return "Star"
    elif not high_growth and leading_share:
        return "Cash Cow"
    elif high_growth and not leading_share:
        return "Question Mark"
    else:
        return "Dog"
def quadrant_emoji(quadrant: str) -> str:
    return {
        "Star": "⭐",
        "Cash Cow": "🐄",
        "Question Mark": "❓",
        "Dog": "🐕",
    }.get(quadrant, "?")
def investment_posture(quadrant: str, qoq_growth: float, retention: Optional[float]) -> str:
    """
    Invest / Maintain / Kill recommendation with nuance.
    """
    if quadrant == "Star":
        return "Invest"
    elif quadrant == "Cash Cow":
        # If cash cow is declining fast or retention is poor, consider killing
        if qoq_growth < -0.10 or (retention is not None and retention < 0.30):
            return "Kill"
        return "Maintain"
    elif quadrant == "Question Mark":
        # Fast QoQ growth signals the bet might pay off → Invest
        # Flat or slow QoQ with weak retention → Kill
        if qoq_growth >= 0.15 and (retention is None or retention >= 0.25):
            return "Invest"
        elif qoq_growth < 0.05 or (retention is not None and retention < 0.20):
            return "Kill"
        return "Evaluate"  # Needs explicit strategic decision
    else:  # Dog
        if qoq_growth > 0.10 and (retention is None or retention >= 0.35):
            return "Evaluate"  # Surprising momentum — verify before killing
        return "Kill"
def posture_color(posture: str) -> str:
    return {
        "Invest": "✓",
        "Maintain": "◑",
        "Kill": "✗",
        "Evaluate": "⚠",
    }.get(posture, "?")
def _compute_alignment(posture: str, eng_pct: float) -> float:
    """
    Returns 0.0-1.0 score. High = engineering allocation matches strategic posture.
    """
    targets = {"Invest": 0.35, "Maintain": 0.15, "Kill": 0.05, "Evaluate": 0.20}
    target = targets.get(posture, 0.20)
    deviation = abs(eng_pct / 100 - target)
    return max(0.0, 1.0 - (deviation / 0.35))

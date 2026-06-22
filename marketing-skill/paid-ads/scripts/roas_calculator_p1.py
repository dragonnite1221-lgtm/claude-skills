# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from roas_calculator_base import *  # noqa: F403,E402


def _roas_label(roas: float) -> str:
    if roas >= 8:
        return "Excellent (8x+)"
    if roas >= 5:
        return "Strong (5-8x)"
    if roas >= 3:
        return "Good (3-5x)"
    if roas >= 2:
        return "Acceptable (2-3x) — check margins"
    if roas >= 1:
        return "Below target (<2x) — likely unprofitable"
    return "Losing money (<1x)"
def _recommendations(metrics: dict, spend: float, margin_pct: float) -> list:
    recs = []

    roas = metrics.get("roas", {}).get("value")
    be_roas = metrics.get("break_even_roas", {}).get("value")

    if roas and be_roas:
        if roas < be_roas:
            shortfall = round((be_roas - roas) * spend, 2)
            recs.append(f"⚠️  Losing ${shortfall:,.2f}/period — pause or restructure campaign immediately")
        elif roas < be_roas * 1.5:
            recs.append("⚠️  Marginally profitable — optimize creatives and targeting before scaling")
        else:
            recs.append("✅  Profitable — consider increasing budget or duplicating campaign")

    cpa = metrics.get("cpa", {}).get("value")
    cpl = metrics.get("cpl", {}).get("value")
    cvr = metrics.get("conversion_rate", {}).get("value")

    if cvr and cvr < 2:
        recs.append(f"⚠️  CVR {cvr}% is low — test new landing pages, headlines, and CTAs")
    elif cvr and cvr >= 5:
        recs.append(f"✅  Strong CVR {cvr}% — maximize traffic to this funnel")

    if cpa and cpl:
        l2c = metrics.get("lead_to_conversion_rate", {}).get("value", 0)
        if l2c < 10:
            recs.append(f"⚠️  Lead-to-close rate {l2c}% is low — review sales qualification or nurture sequence")

    ctr = metrics.get("ctr", {}).get("value")
    if ctr:
        if ctr < 1:
            recs.append(f"⚠️  CTR {ctr}% is low — refresh ad copy and audience targeting")
        elif ctr >= 5:
            recs.append(f"✅  High CTR {ctr}% — strong creative, ensure LP matches ad message")

    if not recs:
        recs.append("Add more data (margin %, impressions, leads) for actionable recommendations")

    return recs

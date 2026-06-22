# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from portfolio_analyzer_base import *  # noqa: F403,E402
# fmt: off
from portfolio_analyzer_p1 import _compute_alignment, bcg_quadrant, investment_posture  # noqa: E402,E501
# fmt: on


def _product_findings(
    quadrant: str, posture: str,
    qoq_growth: float, share_ratio: float, market_growth: float,
    retention: Optional[float], nps: Optional[int], eng_pct: float
) -> list:
    findings = []

    if quadrant == "Star":
        if eng_pct < 30:
            findings.append(f"⚠ Star product getting only {eng_pct}% of eng capacity — likely underinvested. Stars need fuel.")
        else:
            findings.append(f"✓ Star product with {eng_pct}% eng allocation — appropriate investment.")
        if share_ratio < 1.5:
            findings.append(f"◑ Share ratio {share_ratio:.1f}x — leading but not dominant. Accelerate to widen the gap.")
        else:
            findings.append(f"✓ Share ratio {share_ratio:.1f}x — strong lead. Defend aggressively.")

    elif quadrant == "Cash Cow":
        if eng_pct > 25:
            findings.append(f"⚠ Cash Cow getting {eng_pct}% of eng — overinvested. Reduce to 10-15% max. Redeploy to Stars.")
        else:
            findings.append(f"✓ Cash Cow with {eng_pct}% eng — appropriate. Don't innovate, just maintain.")
        if qoq_growth < -0.05:
            findings.append(f"⚠ Revenue declining {abs(qoq_growth):.0%} QoQ — monitor for transition to Dog.")
        else:
            findings.append(f"✓ Revenue stable (QoQ: {qoq_growth:+.0%}) — milk this.")

    elif quadrant == "Question Mark":
        findings.append(f"⚠ Fast market ({market_growth:.0f}% growth) but only {share_ratio:.1f}x relative share.")
        findings.append(f"  Decision required: Invest to capture share or exit. 'Maintain' loses share every quarter.")
        if qoq_growth >= 0.15:
            findings.append(f"✓ QoQ growth {qoq_growth:+.0%} — momentum building. Investment may be justified.")
        elif qoq_growth < 0.05:
            findings.append(f"✗ QoQ growth {qoq_growth:+.0%} — stalled despite hot market. Strong exit signal.")

    elif quadrant == "Dog":
        findings.append(f"✗ Low share ({share_ratio:.1f}x) in slow/declining market ({market_growth:.0f}% growth).")
        if eng_pct > 10:
            findings.append(f"✗ Dog consuming {eng_pct}% of eng capacity. Set a sunset date. Migrate customers.")
        if qoq_growth > 0:
            findings.append(f"◑ Slight QoQ growth ({qoq_growth:+.0%}) — verify whether this is genuine or contract timing.")

    if retention is not None:
        if retention < 0.30:
            findings.append(f"✗ D30 retention {retention:.0%} — users not finding value. Weak unit economics for any posture.")
        elif retention >= 0.50:
            findings.append(f"✓ D30 retention {retention:.0%} — users find value. Supports investment or stable maintenance.")

    if nps is not None:
        if nps < 0:
            findings.append(f"✗ NPS {nps} — net detractors. Word of mouth is negative. Fix before scaling.")
        elif nps >= 40:
            findings.append(f"✓ NPS {nps} — strong promoter base. Harness for referrals.")

    return findings
def analyze_product(p: dict) -> dict:
    revenue_q = p.get("revenue_quarterly", 0)
    revenue_prev = p.get("revenue_prev_q", revenue_q)
    qoq_growth = (revenue_q - revenue_prev) / revenue_prev if revenue_prev else 0.0

    your_share = p.get("your_market_share", 0)
    competitor_share = p.get("largest_competitor_share", 1)
    share_ratio = your_share / competitor_share if competitor_share else 0.0

    market_growth = p.get("market_growth_pct", 0)
    retention = p.get("d30_retention")
    nps = p.get("nps")
    eng_pct = p.get("eng_capacity_pct", 0)

    quadrant = bcg_quadrant(market_growth, share_ratio)
    posture = investment_posture(quadrant, qoq_growth, retention)

    # Alignment score: how well does engineering investment match the recommended posture?
    # Invest products should have high eng allocation; Kill products should have low.
    alignment_score = _compute_alignment(posture, eng_pct)

    return {
        "name": p.get("name", "Unknown"),
        "revenue_quarterly": revenue_q,
        "revenue_prev_q": revenue_prev,
        "qoq_growth": qoq_growth,
        "market_growth_pct": market_growth,
        "your_market_share": your_share,
        "largest_competitor_share": competitor_share,
        "share_ratio": share_ratio,
        "eng_capacity_pct": eng_pct,
        "d30_retention": retention,
        "nps": nps,
        "quadrant": quadrant,
        "posture": posture,
        "alignment_score": alignment_score,
        "notes": p.get("notes", ""),
        "findings": _product_findings(quadrant, posture, qoq_growth, share_ratio,
                                      market_growth, retention, nps, eng_pct),
    }

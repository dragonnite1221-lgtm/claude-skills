# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from portfolio_analyzer_base import *  # noqa: F403,E402
# fmt: off
from portfolio_analyzer_p2 import analyze_product  # noqa: E402,E501
# fmt: on


def _portfolio_health(products: list, total_revenue: float, total_eng: float) -> float:
    """
    Portfolio health 0-1. Penalizes:
    - No Stars (no growth engine)
    - Dogs consuming > 20% of eng
    - Poor alignment scores
    - Revenue concentrated in Dogs/Question Marks
    """
    score = 1.0

    quadrants = [p["quadrant"] for p in products]
    has_star = "Star" in quadrants
    has_cash_cow = "Cash Cow" in quadrants

    if not has_star:
        score -= 0.25  # No growth engine is a serious problem
    if not has_cash_cow:
        score -= 0.10  # No cash generator means funding stars from burn

    # Dog eng allocation penalty
    dog_eng = sum(p["eng_capacity_pct"] for p in products if p["quadrant"] == "Dog")
    if dog_eng > 20:
        score -= 0.20
    elif dog_eng > 10:
        score -= 0.10

    # Revenue in dogs penalty
    if total_revenue > 0:
        dog_rev_pct = sum(p["revenue_quarterly"] for p in products if p["quadrant"] == "Dog") / total_revenue
        if dog_rev_pct > 0.30:
            score -= 0.15

    # Average alignment score
    avg_alignment = sum(p["alignment_score"] for p in products) / len(products) if products else 0
    score -= (1 - avg_alignment) * 0.20

    return max(0.0, min(1.0, score))
def _portfolio_findings(
    products: list, total_revenue: float,
    quadrant_revenue: dict, quadrant_eng: dict
) -> list:
    findings = []

    stars = [p for p in products if p["quadrant"] == "Star"]
    cows = [p for p in products if p["quadrant"] == "Cash Cow"]
    questions = [p for p in products if p["quadrant"] == "Question Mark"]
    dogs = [p for p in products if p["quadrant"] == "Dog"]

    if not stars:
        findings.append("✗ CRITICAL: No Star products. You have no growth engine. Identify a Question Mark to invest in or revisit your market positioning.")
    elif len(stars) == 1:
        findings.append(f"◑ Single Star ({stars[0]['name']}). Portfolio is fragile — one product drives all growth. Diversify.")
    else:
        findings.append(f"✓ {len(stars)} Star products — healthy growth engine.")

    if not cows:
        findings.append("⚠ No Cash Cow products. Stars are consuming capital without a self-funding mechanism. Watch burn rate.")
    else:
        cow_rev = quadrant_revenue.get("Cash Cow", 0)
        cow_pct = cow_rev / total_revenue if total_revenue else 0
        findings.append(f"✓ Cash Cow revenue: {cow_pct:.0%} of total — funds Star investment.")

    if questions:
        findings.append(f"⚠ {len(questions)} Question Mark(s): {', '.join(p['name'] for p in questions)}.")
        findings.append("  Each needs a binary decision: invest to win share, or exit. Set a 2-quarter deadline.")

    if dogs:
        dog_eng_total = sum(p["eng_capacity_pct"] for p in dogs)
        findings.append(f"✗ {len(dogs)} Dog product(s): {', '.join(p['name'] for p in dogs)} consuming {dog_eng_total}% of eng capacity.")
        findings.append(f"  That's {dog_eng_total}% of your engineers on declining products. Set sunset dates.")

    # Alignment check
    misaligned = [p for p in products if p["alignment_score"] < 0.50]
    if misaligned:
        findings.append(f"⚠ Engineering allocation misaligned on: {', '.join(p['name'] for p in misaligned)}.")
        findings.append("  Rebalance: move capacity from Dogs/Cows to Stars.")

    return findings
def analyze_portfolio(data: dict) -> dict:
    products = [analyze_product(p) for p in data.get("products", [])]

    total_revenue = sum(p["revenue_quarterly"] for p in products)
    total_eng = sum(p["eng_capacity_pct"] for p in products)

    # Revenue by quadrant
    quadrant_revenue = {}
    quadrant_eng = {}
    for p in products:
        q = p["quadrant"]
        quadrant_revenue[q] = quadrant_revenue.get(q, 0) + p["revenue_quarterly"]
        quadrant_eng[q] = quadrant_eng.get(q, 0) + p["eng_capacity_pct"]

    # Portfolio health score
    health = _portfolio_health(products, total_revenue, total_eng)

    # Portfolio-level findings
    portfolio_findings = _portfolio_findings(products, total_revenue, quadrant_revenue, quadrant_eng)

    return {
        "company": data.get("company", "Unknown"),
        "total_engineering_headcount": data.get("total_engineering_headcount"),
        "products": products,
        "total_revenue_quarterly": total_revenue,
        "quadrant_summary": {
            q: {
                "count": sum(1 for p in products if p["quadrant"] == q),
                "revenue": quadrant_revenue.get(q, 0),
                "revenue_pct": quadrant_revenue.get(q, 0) / total_revenue if total_revenue else 0,
                "eng_pct": quadrant_eng.get(q, 0),
            }
            for q in ["Star", "Cash Cow", "Question Mark", "Dog"]
        },
        "portfolio_health_score": health,
        "portfolio_findings": portfolio_findings,
    }
def fmt_currency(n: float) -> str:
    if n >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"${n/1_000:.0f}K"
    return f"${n:.0f}"

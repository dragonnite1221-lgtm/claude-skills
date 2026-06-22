# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from expansion_opportunity_scorer_base import *  # noqa: F403,E402
# fmt: off
from expansion_opportunity_scorer_p1 import clamp, estimate_department_expansion_revenue, estimate_module_revenue, estimate_seat_expansion_revenue, estimate_tier_upgrade_revenue, safe_divide  # noqa: E402,E501
# fmt: on


def priority_score(revenue: float, effort: str) -> float:
    """Calculate priority score (higher = better).

    Favours high revenue with low effort.
    """
    effort_multiplier = {"low": 3.0, "medium": 2.0, "high": 1.0}
    mult = effort_multiplier.get(effort.lower(), 1.0)
    # Normalise revenue to a 0-100 scale (assume max single opportunity is $200k)
    rev_score = clamp(safe_divide(revenue, 2000.0))  # $200k => 100
    return round(rev_score * mult, 1)
def analyse_expansion(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse expansion opportunities for a single customer."""
    arr = customer.get("arr", 0)
    segment = customer.get("segment", "mid-market").lower()
    contract = customer.get("contract", {})
    product_usage = customer.get("product_usage", {})
    departments = customer.get("departments", {})

    all_opportunities: List[Dict[str, Any]] = []

    # 1. Seat expansion
    licensed = contract.get("licensed_seats", 0)
    active = contract.get("active_seats", 0)
    seat_rev, seat_rationale = estimate_seat_expansion_revenue(arr, licensed, active, segment)
    if seat_rev > 0:
        all_opportunities.append({
            "type": "expansion",
            "category": "seat_expansion",
            "estimated_revenue": seat_rev,
            "effort": "low",
            "rationale": seat_rationale,
            "priority_score": priority_score(seat_rev, "low"),
        })

    # 2. Tier upgrade
    current_tier = contract.get("plan_tier", "").lower()
    available_tiers = contract.get("available_tiers", [])
    tier_rev, target_tier, tier_rationale = estimate_tier_upgrade_revenue(arr, current_tier, available_tiers)
    if tier_rev > 0 and target_tier:
        all_opportunities.append({
            "type": "upsell",
            "category": "tier_upgrade",
            "target_tier": target_tier,
            "estimated_revenue": tier_rev,
            "effort": "medium",
            "rationale": tier_rationale,
            "priority_score": priority_score(tier_rev, "medium"),
        })

    # 3. Module cross-sell
    module_opps = estimate_module_revenue(arr, product_usage)
    for opp in module_opps:
        opp["category"] = "module_cross_sell"
        opp["priority_score"] = priority_score(opp["estimated_revenue"], opp["effort"])
        all_opportunities.append(opp)

    # 4. Department expansion
    current_depts = departments.get("current", [])
    potential_depts = departments.get("potential", [])
    dept_opps = estimate_department_expansion_revenue(arr, current_depts, potential_depts, segment)
    for opp in dept_opps:
        opp["category"] = "department_expansion"
        opp["priority_score"] = priority_score(opp["estimated_revenue"], opp["effort"])
        all_opportunities.append(opp)

    # Sort by priority score descending
    all_opportunities.sort(key=lambda o: o["priority_score"], reverse=True)

    # Adoption depth summary
    total_modules = len(product_usage)
    adopted_modules = sum(1 for m in product_usage.values() if m.get("adopted", False))
    avg_usage = round(
        safe_divide(
            sum(m.get("usage_pct", 0) for m in product_usage.values() if m.get("adopted", False)),
            max(adopted_modules, 1),
        ),
        1,
    )

    total_estimated_revenue = sum(o["estimated_revenue"] for o in all_opportunities)

    return {
        "customer_id": customer.get("customer_id", "unknown"),
        "name": customer.get("name", "Unknown"),
        "segment": segment,
        "arr": arr,
        "adoption_summary": {
            "total_modules": total_modules,
            "adopted_modules": adopted_modules,
            "adoption_rate": round(safe_divide(adopted_modules, total_modules) * 100, 1) if total_modules > 0 else 0,
            "avg_usage_pct": avg_usage,
            "seat_utilisation": round(safe_divide(active, max(licensed, 1)) * 100, 1),
            "current_tier": current_tier,
            "departments_covered": len(current_depts),
            "departments_potential": len(potential_depts),
        },
        "total_estimated_revenue": round(total_estimated_revenue, 0),
        "opportunity_count": len(all_opportunities),
        "opportunities": all_opportunities,
    }

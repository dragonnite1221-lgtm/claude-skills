# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from expansion_opportunity_scorer_base import *  # noqa: F403,E402


TIER_UPLIFT: Dict[str, float] = {
    "starter": 1.0,
    "professional": 1.8,
    "enterprise": 3.0,
    "enterprise_plus": 4.5,
}
MODULE_REVENUE_FRACTION: Dict[str, float] = {
    "core_platform": 0.00,        # Already included in base
    "analytics_module": 0.15,
    "integrations_module": 0.12,
    "api_access": 0.10,
    "advanced_reporting": 0.18,
    "security_module": 0.20,
    "automation_module": 0.15,
    "collaboration_module": 0.10,
    "data_export": 0.08,
    "custom_workflows": 0.22,
    "sso_module": 0.08,
    "audit_module": 0.10,
}
EFFORT_MAP: Dict[str, str] = {
    "upsell_tier": "medium",
    "cross_sell_module": "low",
    "seat_expansion": "low",
    "department_expansion": "high",
}
HIGH_USAGE_THRESHOLD = 75   # % usage indicates readiness for more
LOW_ADOPTION_THRESHOLD = 30  # % usage is too low to push expansion there
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Return numerator / denominator, or *default* when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp *value* between *lo* and *hi*."""
    return max(lo, min(hi, value))
def estimate_seat_expansion_revenue(
    arr: float, licensed: int, active: int, segment: str
) -> Tuple[float, str]:
    """Estimate revenue from seat expansion.

    Returns (estimated_revenue, rationale).
    """
    utilisation = safe_divide(active, licensed)
    if utilisation >= 0.90:
        # Near capacity -- likely needs more seats
        growth_factor = {"enterprise": 0.25, "mid-market": 0.20, "smb": 0.15}
        factor = growth_factor.get(segment.lower(), 0.15)
        revenue = round(arr * factor, 0)
        return revenue, f"Seat utilisation at {utilisation:.0%} -- likely needs {int(licensed * factor)} additional seats"
    return 0.0, f"Seat utilisation at {utilisation:.0%} -- not yet at expansion threshold"
def estimate_tier_upgrade_revenue(
    arr: float, current_tier: str, available_tiers: List[str]
) -> Tuple[float, Optional[str], str]:
    """Estimate revenue from tier upgrade.

    Returns (estimated_revenue, target_tier, rationale).
    """
    current_mult = TIER_UPLIFT.get(current_tier.lower(), 1.0)
    best_revenue = 0.0
    best_tier = None
    rationale = "Already on highest tier"

    for tier in available_tiers:
        tier_mult = TIER_UPLIFT.get(tier.lower(), 1.0)
        if tier_mult > current_mult:
            # Calculate revenue as the incremental ARR from upgrading
            base_arr = safe_divide(arr, current_mult)
            upgrade_arr = base_arr * tier_mult
            incremental = upgrade_arr - arr
            if incremental > best_revenue:
                # Pick the next tier up (not skip tiers)
                if best_tier is None or tier_mult < TIER_UPLIFT.get(best_tier.lower(), 999):
                    best_revenue = round(incremental, 0)
                    best_tier = tier
                    rationale = f"Upgrade from {current_tier} to {tier} adds ${incremental:,.0f} ARR"

    return best_revenue, best_tier, rationale
def estimate_module_revenue(
    arr: float, product_usage: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Identify cross-sell opportunities from unadopted modules.

    Returns list of opportunity dicts.
    """
    opportunities: List[Dict[str, Any]] = []

    for module_name, module_data in product_usage.items():
        adopted = module_data.get("adopted", False)
        usage_pct = module_data.get("usage_pct", 0)
        fraction = MODULE_REVENUE_FRACTION.get(module_name.lower(), 0.10)

        if not adopted and fraction > 0:
            revenue = round(arr * fraction, 0)
            opportunities.append({
                "module": module_name,
                "type": "cross_sell",
                "estimated_revenue": revenue,
                "effort": "low",
                "rationale": f"Module not adopted -- ${revenue:,.0f} potential ARR",
            })
        elif adopted and usage_pct < LOW_ADOPTION_THRESHOLD and fraction > 0:
            # Already adopted but underutilised -- focus on enablement, not expansion
            pass  # Skip -- needs enablement, not a sales motion

    return opportunities
def estimate_department_expansion_revenue(
    arr: float,
    current_departments: List[str],
    potential_departments: List[str],
    segment: str,
) -> List[Dict[str, Any]]:
    """Estimate revenue from expanding to new departments."""
    opportunities: List[Dict[str, Any]] = []
    current_set = {d.lower() for d in current_departments}
    per_dept_estimate = safe_divide(arr, max(len(current_departments), 1))

    for dept in potential_departments:
        if dept.lower() not in current_set:
            # Estimate each new department at the average per-department ARR
            revenue = round(per_dept_estimate * 0.8, 0)  # Slight discount for new dept
            opportunities.append({
                "department": dept,
                "type": "expansion",
                "estimated_revenue": revenue,
                "effort": "high",
                "rationale": f"Expand to {dept} department -- est. ${revenue:,.0f} ARR",
            })

    return opportunities

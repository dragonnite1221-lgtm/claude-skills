# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scenario_modeler_base import *  # noqa: F403,E402


class Severity(Enum):
    BASE = "base"       # One variable hits
    STRESS = "stress"   # Two variables hit
    SEVERE = "severe"   # All variables hit
class Domain(Enum):
    FINANCIAL = "Financial (CFO)"
    REVENUE = "Revenue (CRO)"
    PRODUCT = "Product (CPO)"
    ENGINEERING = "Engineering (CTO)"
    PEOPLE = "People (CHRO)"
    OPERATIONS = "Operations (COO)"
    SECURITY = "Security (CISO)"
    MARKET = "Market (CMO)"
@dataclass
class Variable:
    name: str
    description: str
    probability: float          # 0.0-1.0
    arrt_impact_pct: float      # % of ARR at risk (negative = loss)
    runway_impact_months: float # months lost from runway (negative = reduction)
    affected_domains: List[Domain]
    timeline_days: int          # when it hits
@dataclass
class CascadeEffect:
    trigger_domain: Domain
    caused_domain: Domain
    mechanism: str              # how A causes B
    severity_multiplier: float  # compounds the base impact
@dataclass
class Hedge:
    action: str
    cost_usd: int
    impact_description: str
    owner: str
    deadline_days: int
    reduces_probability: float  # how much it reduces scenario probability
@dataclass
class Scenario:
    name: str
    variables: List[Variable]
    cascades: List[CascadeEffect]
    hedges: List[Hedge]
    # Company baseline
    current_arr_usd: int = 2_000_000
    current_runway_months: int = 14
    monthly_burn_usd: int = 140_000
def calculate_impact(
    scenario: Scenario,
    severity: Severity
) -> Dict:
    """Calculate combined impact for a given severity level."""
    variables = scenario.variables

    # Select variables by severity
    if severity == Severity.BASE:
        active_vars = variables[:1]
    elif severity == Severity.STRESS:
        active_vars = variables[:2]
    else:
        active_vars = variables

    # Direct impacts
    total_arr_loss_pct = sum(abs(v.arrt_impact_pct) for v in active_vars)
    total_runway_reduction = sum(abs(v.runway_impact_months) for v in active_vars)

    arr_at_risk = scenario.current_arr_usd * (total_arr_loss_pct / 100)
    new_arr = scenario.current_arr_usd - arr_at_risk
    new_runway = scenario.current_runway_months - total_runway_reduction

    # Cascade multiplier (stress/severe amplify via domain cascades)
    cascade_multiplier = 1.0
    if len(active_vars) > 1:
        active_domains = set(d for v in active_vars for d in v.affected_domains)
        for cascade in scenario.cascades:
            if (cascade.trigger_domain in active_domains and
                    cascade.caused_domain in active_domains):
                cascade_multiplier *= cascade.severity_multiplier

    # Apply cascade
    effective_arr_loss = arr_at_risk * cascade_multiplier
    effective_arr = scenario.current_arr_usd - effective_arr_loss
    effective_runway = max(0, new_runway - (cascade_multiplier - 1.0) * 2)

    # New burn multiple
    new_monthly_burn = scenario.monthly_burn_usd * cascade_multiplier
    burn_multiple = (new_monthly_burn * 12) / max(effective_arr, 1)

    # Affected domains
    affected = set(d for v in active_vars for d in v.affected_domains)

    return {
        "severity": severity.value,
        "active_variables": [v.name for v in active_vars],
        "arr_at_risk_usd": int(effective_arr_loss),
        "arr_at_risk_pct": round(effective_arr_loss / scenario.current_arr_usd * 100, 1),
        "projected_arr_usd": int(effective_arr),
        "runway_months": round(effective_runway, 1),
        "runway_change": round(effective_runway - scenario.current_runway_months, 1),
        "cascade_multiplier": round(cascade_multiplier, 2),
        "new_burn_multiple": round(burn_multiple, 1),
        "affected_domains": [d.value for d in affected],
        "existential_risk": effective_runway < 6.0,
        "board_escalation_required": effective_runway < 9.0,
    }

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402


@dataclass
class BandDefinition:
    """Salary band for a role level."""
    level: str          # L1, L2, L3, L4, M1, M2, M3, VP
    function: str       # Engineering, Sales, Product, G&A, Marketing, CS
    band_min: int       # Annual USD
    band_mid: int       # P50 anchor
    band_max: int       # Band ceiling
    market_p25: int     # Market 25th percentile
    market_p50: int     # Market median (should align with band_mid for P50 strategy)
    market_p75: int     # Market 75th percentile
    location_zone: str  # Tier1 (SF/NYC), Tier2 (Austin/Denver), Tier3 (Remote/other), EU
@dataclass
class Employee:
    """One employee record."""
    id: str
    name: str
    role: str
    level: str
    function: str
    location_zone: str
    base_salary: int
    bonus_target_pct: float   # % of base
    equity_shares: int        # Total unvested options/RSUs
    equity_strike: float      # Strike price (0 for RSUs)
    equity_current_409a: float  # Current 409A share price
    equity_vest_years_remaining: float  # How many years of vesting remain
    benefits_annual: int      # Employer-paid benefits cost
    gender: str               # M/F/NB/Undisclosed (for equity audit)
    ethnicity: str            # For equity audit — can be "Undisclosed"
    tenure_years: float
    performance_rating: int   # 1–5
    last_raise_months_ago: int
    last_equity_refresh_months_ago: Optional[int] = None
@dataclass
class CompRoster:
    company: str
    as_of_date: str             # ISO date
    funding_stage: str          # Seed, Series A, Series B, etc.
    comp_philosophy_target: str # P50, P65, P75 — your target percentile
    preferred_stock_price: float  # Last round price (for offer modeling)
    employees: list[Employee] = field(default_factory=list)
    bands: list[BandDefinition] = field(default_factory=list)
def find_band(roster: CompRoster, level: str, function: str, zone: str) -> Optional[BandDefinition]:
    """Find best-matching band. Falls back to any matching level+function if zone not found."""
    matches = [b for b in roster.bands if b.level == level and b.function == function and b.location_zone == zone]
    if matches:
        return matches[0]
    # Fallback: same level+function, any zone
    matches = [b for b in roster.bands if b.level == level and b.function == function]
    if matches:
        return matches[0]
    # Fallback: same level, any function
    matches = [b for b in roster.bands if b.level == level]
    if matches:
        return matches[0]
    return None
def compa_ratio(salary: int, band_mid: int) -> float:
    return salary / band_mid if band_mid > 0 else 0.0
def band_position(salary: int, band_min: int, band_max: int) -> float:
    """Position in band: 0.0 = at min, 1.0 = at max."""
    if band_max == band_min:
        return 0.5
    return (salary - band_min) / (band_max - band_min)
def annualized_equity_value(emp: Employee) -> int:
    """Current 409A value of unvested equity, annualized."""
    if emp.equity_vest_years_remaining <= 0:
        return 0
    if emp.equity_current_409a > emp.equity_strike:
        intrinsic = (emp.equity_current_409a - emp.equity_strike) * emp.equity_shares
    else:
        # Options underwater — still show at current FMV for RSUs or future value for options
        intrinsic = emp.equity_current_409a * emp.equity_shares if emp.equity_strike == 0 else 0
    return int(intrinsic / emp.equity_vest_years_remaining)
def total_comp(emp: Employee) -> int:
    bonus = int(emp.base_salary * emp.bonus_target_pct)
    equity = annualized_equity_value(emp)
    return emp.base_salary + bonus + equity + emp.benefits_annual

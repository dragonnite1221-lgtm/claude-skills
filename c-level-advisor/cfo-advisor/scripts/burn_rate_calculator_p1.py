# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from burn_rate_calculator_base import *  # noqa: F403,E402


@dataclass
class HiringEntry:
    """A planned hire."""
    month: int          # months from model start (1-indexed)
    role: str
    department: str     # "sales", "engineering", "cs", "ga"
    annual_salary: float
    benefits_pct: float = 0.22  # benefits as % of salary
    recruiting_cost: float = 0.0  # one-time recruiting fee
@dataclass
class RevenueEntry:
    """Monthly revenue data point (historical or projected)."""
    month: int
    mrr: float          # monthly recurring revenue
    one_time: float = 0.0
@dataclass
class ModelConfig:
    """Master configuration for a runway scenario."""
    name: str
    starting_cash: float
    starting_mrr: float
    starting_headcount: int
    avg_loaded_salary: float        # average fully-loaded salary per current employee
    base_non_headcount_opex: float  # monthly non-headcount costs (infra, tools, etc.)
    gross_margin_pct: float         # 0.0–1.0
    mrr_growth_rate: float          # monthly MoM growth rate, 0.0–1.0
    hiring_plan: list[HiringEntry] = field(default_factory=list)
    model_months: int = 24
    start_date: Optional[date] = None
@dataclass
class MonthResult:
    """Single month output."""
    month: int
    label: str              # e.g. "Month 1 (Apr 2025)"
    mrr: float
    gross_profit: float
    headcount: int
    headcount_cost: float   # total loaded headcount cost this month
    other_opex: float
    gross_burn: float
    net_burn: float
    cash_start: float
    cash_end: float
    runway_months: float    # projected runway from this month
    cumulative_new_arr: float   # for burn multiple

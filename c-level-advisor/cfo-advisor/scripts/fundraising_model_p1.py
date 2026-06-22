# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fundraising_model_base import *  # noqa: F403,E402


@dataclass
class Shareholder:
    """A shareholder in the cap table."""
    name: str
    share_class: str        # "common", "preferred", "option"
    shares: float
    invested: float = 0.0   # total cash invested
    is_option_pool: bool = False
@dataclass
class RoundConfig:
    """Configuration for a financing round."""
    name: str                       # e.g. "Series A"
    pre_money_valuation: float
    investment_amount: float
    new_option_pool_pct: float = 0.0    # % of POST-money to allocate to new options
    option_pool_pre_round: bool = True  # True = pool created before round (dilutes founders)
    lead_investor_name: str = "New Investor"
    share_price_override: Optional[float] = None  # if None, computed from valuation
@dataclass
class CapTableEntry:
    """A row in the cap table at a point in time."""
    name: str
    share_class: str
    shares: float
    pct_ownership: float
    invested: float
    is_option_pool: bool = False
@dataclass
class RoundResult:
    """Snapshot of cap table after a round closes."""
    round_name: str
    pre_money_valuation: float
    investment_amount: float
    post_money_valuation: float
    price_per_share: float
    new_shares_issued: float
    option_pool_shares_created: float
    total_shares: float
    cap_table: list[CapTableEntry]
@dataclass
class ExitAnalysis:
    """Proceeds to each shareholder at an exit."""
    exit_valuation: float
    shareholder: str
    shares: float
    ownership_pct: float
    proceeds_common: float          # if all preferred converts to common
    invested: float
    moic: float                     # multiple on invested capital (for investors)

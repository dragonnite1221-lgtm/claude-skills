# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_analyzer_base import *  # noqa: F403,E402


@dataclass
class CohortData:
    """
    Revenue data for a group of customers acquired in the same period.
    Revenue is tracked monthly: revenue[0] = month 1, revenue[1] = month 2, etc.
    """
    label: str                      # e.g. "Q1 2024"
    acquisition_period: str         # human-readable label
    customers_acquired: int
    total_cac_spend: float          # total S&M spend to acquire this cohort
    monthly_revenue: list[float]    # revenue per month from this cohort
    gross_margin_pct: float = 0.70  # blended gross margin for this cohort
@dataclass
class ChannelData:
    """Acquisition cost and customer data for a single channel."""
    channel: str
    spend: float
    customers_acquired: int
    avg_arpa: float                 # average revenue per account (monthly)
    gross_margin_pct: float = 0.70
    avg_monthly_churn: float = 0.02 # monthly churn rate for customers from this channel
@dataclass
class UnitEconomicsResult:
    """Computed unit economics for a cohort or channel."""
    label: str
    customers: int
    cac: float
    arpa: float                 # average revenue per account per month
    gross_margin_pct: float
    monthly_churn: float
    ltv: float
    ltv_cac_ratio: float
    payback_months: float
    # Cohort-specific
    m1_revenue: Optional[float] = None
    m6_revenue: Optional[float] = None
    m12_revenue: Optional[float] = None
    m24_revenue: Optional[float] = None
    m12_ltv: Optional[float] = None   # realized LTV through month 12
    retention_m6: Optional[float] = None    # % of M1 revenue retained at M6
    retention_m12: Optional[float] = None
def calc_ltv(arpa: float, gross_margin_pct: float, monthly_churn: float) -> float:
    """
    LTV = (ARPA × Gross Margin) / Monthly Churn Rate
    Assumes constant churn (simplified; cohort method is more accurate).
    """
    if monthly_churn <= 0:
        return float("inf")
    return (arpa * gross_margin_pct) / monthly_churn
def calc_payback(cac: float, arpa: float, gross_margin_pct: float) -> float:
    """
    CAC Payback (months) = CAC / (ARPA × Gross Margin)
    """
    denominator = arpa * gross_margin_pct
    if denominator <= 0:
        return float("inf")
    return cac / denominator

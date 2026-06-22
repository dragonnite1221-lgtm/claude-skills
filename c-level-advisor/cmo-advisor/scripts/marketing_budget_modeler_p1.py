# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from marketing_budget_modeler_base import *  # noqa: F403,E402


@dataclass
class Channel:
    name: str
    cac: float              # Customer acquisition cost ($)
    max_mqls_per_month: int # Realistic capacity ceiling (MQLs/month)
    mql_to_close_rate: float  # Combined MQL → closed-won rate (0.0–1.0)
    payback_months: float   # Based on ARPU × gross margin
    ltv: float              # Lifetime value ($)
    trend: str = "stable"   # "improving" | "stable" | "declining"
@dataclass
class FunnelRates:
    mql_to_sal: float     # MQL → Sales Accepted Lead
    sal_to_sql: float     # SAL → Sales Qualified Lead
    sql_to_opp: float     # SQL → Opportunity
    opp_to_close: float   # Opportunity → Closed-Won

    @property
    def mql_to_close(self) -> float:
        return self.mql_to_sal * self.sal_to_sql * self.sql_to_opp * self.opp_to_close
@dataclass
class ScenarioResult:
    name: str
    total_budget: float
    channel_budgets: Dict[str, float]
    channel_mqls: Dict[str, int]
    projected_customers: int
    projected_arr: float
    blended_cac: float
    notes: List[str] = field(default_factory=list)
TARGET_NEW_ARR = 3_000_000      # New ARR to generate this year ($)
ASP_ANNUAL = 18_000             # Average annual contract value ($)
GROSS_MARGIN = 0.75             # Product gross margin (%)
ARPU_MONTHLY = ASP_ANNUAL / 12  # Monthly revenue per account
FUNNEL = FunnelRates(
    mql_to_sal=0.65,
    sal_to_sql=0.45,
    sql_to_opp=0.75,
    opp_to_close=0.27,
)
MONTHLY_CHURN = 0.012   # ~14% annual churn
LTV = (ARPU_MONTHLY * GROSS_MARGIN) / MONTHLY_CHURN
CHANNELS: List[Channel] = [
    Channel(
        name="Organic SEO",
        cac=1_800,
        max_mqls_per_month=80,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(1_800 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="improving",
    ),
    Channel(
        name="Paid Search",
        cac=6_200,
        max_mqls_per_month=60,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(6_200 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="stable",
    ),
    Channel(
        name="Paid Social (LinkedIn)",
        cac=8_500,
        max_mqls_per_month=35,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(8_500 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="declining",
    ),
    Channel(
        name="Outbound SDR",
        cac=5_100,
        max_mqls_per_month=50,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(5_100 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="stable",
    ),
    Channel(
        name="Events / Field",
        cac=9_800,
        max_mqls_per_month=25,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(9_800 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="stable",
    ),
    Channel(
        name="Partner / Channel",
        cac=3_400,
        max_mqls_per_month=30,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(3_400 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="improving",
    ),
    Channel(
        name="Content / Inbound",
        cac=2_600,
        max_mqls_per_month=45,
        mql_to_close_rate=FUNNEL.mql_to_close,
        payback_months=(2_600 / (ARPU_MONTHLY * GROSS_MARGIN)),
        ltv=LTV,
        trend="improving",
    ),
]
def customers_needed(target_arr: float, asp: float) -> int:
    return math.ceil(target_arr / asp)
def mqls_needed_total(customers: int, mql_to_close: float) -> int:
    return math.ceil(customers / mql_to_close)
def ltv_to_cac(ltv: float, cac: float) -> float:
    return ltv / cac if cac > 0 else 0.0
def score_channel(ch: Channel) -> float:
    """
    Score a channel for budget priority.
    Higher = more efficient. Used to rank allocation order.
    Factors: LTV:CAC ratio, trend multiplier, capacity.
    """
    ratio = ltv_to_cac(ch.ltv, ch.cac)
    trend_mult = {"improving": 1.2, "stable": 1.0, "declining": 0.7}.get(ch.trend, 1.0)
    return ratio * trend_mult

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from growth_model_simulator_base import *  # noqa: F403,E402


@dataclass
class ChannelSource:
    name: str
    pct_of_new_mrr: float      # Current share of new MRR (0.0–1.0)
    monthly_growth_rate: float  # How fast this channel grows month-over-month
    cac: float                  # CAC in dollars
    payback_months: float       # Months to recover CAC
@dataclass
class GrowthModel:
    name: str
    description: str
    channel_mix: Dict[str, float]  # channel name → % of new MRR
    new_mrr_monthly_base: float    # Starting new MRR/month from this model
    monthly_acceleration: float    # Acceleration factor (compounding)
    avg_ltv_cac: float             # Expected LTV:CAC at scale
    months_to_steady_state: int    # Months before model hits its natural growth rate
    notes: List[str] = field(default_factory=list)
@dataclass
class MonthSnapshot:
    month: int
    mrr: float
    new_mrr: float
    churned_mrr: float
    expansion_mrr: float
    net_new_mrr: float
    cumulative_cac_spend: float
@dataclass
class ModelProjection:
    model: GrowthModel
    snapshots: List[MonthSnapshot]
    break_even_month: Optional[int]  # Month when cumulative revenue > cumulative CAC
STARTING_MRR = 85_000         # Current MRR ($)
MONTHLY_CHURN_RATE = 0.012    # Monthly churn rate (1.2% = ~14% annual)
EXPANSION_RATE = 0.008        # Monthly expansion MRR as % of existing MRR
GROSS_MARGIN = 0.75
SIMULATION_MONTHS = 18
CHANNELS: List[ChannelSource] = [
    ChannelSource("Organic/SEO",      pct_of_new_mrr=0.28, monthly_growth_rate=0.04, cac=1_800,  payback_months=9),
    ChannelSource("PLG Self-Serve",   pct_of_new_mrr=0.15, monthly_growth_rate=0.08, cac=900,   payback_months=5),
    ChannelSource("Outbound SDR",     pct_of_new_mrr=0.25, monthly_growth_rate=0.02, cac=5_100,  payback_months=21),
    ChannelSource("Paid Search",      pct_of_new_mrr=0.15, monthly_growth_rate=0.01, cac=6_200,  payback_months=26),
    ChannelSource("Events/Field",     pct_of_new_mrr=0.08, monthly_growth_rate=0.01, cac=9_800,  payback_months=41),
    ChannelSource("Partner/Channel",  pct_of_new_mrr=0.09, monthly_growth_rate=0.05, cac=3_400,  payback_months=14),
]
GROWTH_MODELS: List[GrowthModel] = [
    GrowthModel(
        name="Current Mix",
        description="Baseline — maintain current channel allocation",
        channel_mix={"Organic/SEO": 0.28, "PLG Self-Serve": 0.15, "Outbound SDR": 0.25,
                     "Paid Search": 0.15, "Events/Field": 0.08, "Partner/Channel": 0.09},
        new_mrr_monthly_base=12_000,
        monthly_acceleration=0.025,
        avg_ltv_cac=3.2,
        months_to_steady_state=3,
        notes=["Baseline. No changes to channel mix."],
    ),
    GrowthModel(
        name="PLG-First",
        description="Shift budget toward PLG self-serve and organic; reduce paid and outbound",
        channel_mix={"Organic/SEO": 0.35, "PLG Self-Serve": 0.35, "Outbound SDR": 0.10,
                     "Paid Search": 0.08, "Events/Field": 0.04, "Partner/Channel": 0.08},
        new_mrr_monthly_base=9_500,   # Slower start — PLG takes time to activate
        monthly_acceleration=0.048,   # But compounds faster
        avg_ltv_cac=5.8,
        months_to_steady_state=6,     # PLG loops take time to build
        notes=[
            "Lower new MRR in months 1-6 while PLG loops activate.",
            "Acceleration compounds strongly after month 6.",
            "Requires product investment in activation/onboarding.",
            "Best fit if time-to-value < 30 min and viral coefficient > 0.3.",
        ],
    ),
    GrowthModel(
        name="Sales-Led Scale",
        description="Double down on outbound SDR and field; optimize for enterprise ACV",
        channel_mix={"Organic/SEO": 0.20, "PLG Self-Serve": 0.05, "Outbound SDR": 0.40,
                     "Paid Search": 0.15, "Events/Field": 0.15, "Partner/Channel": 0.05},
        new_mrr_monthly_base=15_000,  # Higher new MRR from enterprise ACV
        monthly_acceleration=0.018,   # Linear growth — headcount-constrained
        avg_ltv_cac=2.8,
        months_to_steady_state=2,
        notes=[
            "Fastest short-term new MRR if ACV > $30K.",
            "Growth is linear — adds headcount to add pipeline.",
            "CAC and payback worsen as SDR market tightens.",
            "Requires sales capacity increase to sustain.",
        ],
    ),
    GrowthModel(
        name="Community-Led",
        description="Invest in community and content; reduce paid; long-term brand play",
        channel_mix={"Organic/SEO": 0.45, "PLG Self-Serve": 0.15, "Outbound SDR": 0.15,
                     "Paid Search": 0.05, "Events/Field": 0.10, "Partner/Channel": 0.10},
        new_mrr_monthly_base=7_000,   # Slowest start
        monthly_acceleration=0.038,
        avg_ltv_cac=4.5,
        months_to_steady_state=9,     # Community takes longest to activate
        notes=[
            "Lowest new MRR in months 1-9.",
            "Community trust drives lower CAC and higher retention at scale.",
            "Best for categories where buyers seek peer validation.",
            "Requires dedicated community manager from day one.",
        ],
    ),
    GrowthModel(
        name="Hybrid PLS",
        description="PLG self-serve for SMB + sales-assisted for enterprise (Product-Led Sales)",
        channel_mix={"Organic/SEO": 0.30, "PLG Self-Serve": 0.28, "Outbound SDR": 0.22,
                     "Paid Search": 0.08, "Events/Field": 0.06, "Partner/Channel": 0.06},
        new_mrr_monthly_base=11_000,
        monthly_acceleration=0.035,
        avg_ltv_cac=4.1,
        months_to_steady_state=4,
        notes=[
            "PLG handles SMB; sales closes enterprise with PQL signals.",
            "Requires clear PQL definition and SDR/PLG handoff process.",
            "Best if you have a product with both bottom-up and top-down adoption.",
        ],
    ),
]
def _weighted_cac(channel_mix: Dict[str, float]) -> float:
    channel_cac = {ch.name: ch.cac for ch in CHANNELS}
    total = sum(
        channel_mix.get(name, 0) * cac
        for name, cac in channel_cac.items()
    )
    weight_sum = sum(channel_mix.values())
    return total / weight_sum if weight_sum > 0 else 5_000

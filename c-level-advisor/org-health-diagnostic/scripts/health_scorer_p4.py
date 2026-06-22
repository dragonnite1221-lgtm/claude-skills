# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_scorer_base import *  # noqa: F403,E402
# fmt: off
from health_scorer_p1 import Dimension, Stage, TrafficLight, Trend  # noqa: E402,E501
# fmt: on


def to_json(dimensions: List[Dimension], overall: Optional[float], stage: Stage) -> Dict:
    result = {
        "stage": stage.value,
        "overall_score": overall,
        "overall_traffic_light": (
            TrafficLight.GREEN if overall and overall >= 7
            else TrafficLight.YELLOW if overall and overall >= 4
            else TrafficLight.RED
        ).value if overall else "unknown",
        "dimensions": {}
    }
    for dim in dimensions:
        result["dimensions"][dim.key] = {
            "name": dim.name,
            "owner": dim.owner,
            "score": dim.score(),
            "traffic_light": dim.traffic_light().value,
            "trend": dim.trend.value,
            "coverage_pct": round(dim.coverage() * 100),
            "missing_metrics": dim.missing_metrics(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "score": m.score(),
                    "traffic_light": m.traffic_light().value if m.traffic_light() else None,
                }
                for m in dim.metrics
            ]
        }
    return result
def build_sample_data(stage: Stage) -> Dict:
    """Sample Series A company data."""
    return dict(
        # Financial
        runway=14, burn_multiple=1.8, gross_margin=68, mom_growth=8.5,
        revenue_concentration=28, financial_trend=Trend.STABLE,
        # Revenue
        nrr=104, logo_churn=8, pipeline_coverage=1.9, cac_payback=16,
        win_rate=22, revenue_trend=Trend.DECLINING,
        # Product
        nps=38, dau_mau=32, feature_adoption=52, csat=4.1,
        ttv_days=6, product_trend=Trend.STABLE,
        # Engineering
        deploy_freq=3, change_failure_rate=9, mttr_hours=2.8,
        tech_debt_pct=30, incidents_monthly=2, engineering_trend=Trend.STABLE,
        # People
        attrition=21, enps=12, ttf_days=58, internal_promo_rate=18,
        people_trend=Trend.DECLINING,
        # Operations
        okr_completion=62, decision_hours=72, process_maturity=2.5,
        xfn_delivery_rate=65, ops_trend=Trend.STABLE,
        # Security
        incidents_90d=0, mfa_coverage=88, training_completion=82,
        cve_patch_rate=95, pentest_months=14, security_trend=Trend.IMPROVING,
        # Market
        organic_pipeline_pct=35, competitive_win_rate=42,
        cac_trend_score=3, market_trend=Trend.STABLE,
    )
def interactive_mode(stage: Stage) -> Dict:
    """Guided metric entry."""
    print("\nEnter metrics (press Enter to skip):\n")
    data = {}

    def ask(prompt: str, key: str, default=None):
        val = input(f"  {prompt}: ").strip()
        if val:
            try:
                data[key] = float(val)
            except ValueError:
                pass

    print("💰 FINANCIAL")
    ask("Runway (months)", "runway")
    ask("Burn multiple (e.g. 1.8)", "burn_multiple")
    ask("Gross margin (%)", "gross_margin")
    ask("MoM growth (%)", "mom_growth")
    ask("Top customer % of ARR", "revenue_concentration")

    print("\n📈 REVENUE")
    ask("NRR (%)", "nrr")
    ask("Logo churn (%/yr)", "logo_churn")
    ask("Pipeline coverage (x)", "pipeline_coverage")
    ask("CAC payback (months)", "cac_payback")
    ask("Win rate (%)", "win_rate")

    print("\n🚀 PRODUCT")
    ask("NPS score", "nps")
    ask("DAU/MAU (%)", "dau_mau")
    ask("Core feature adoption (%)", "feature_adoption")

    print("\n⚙️  ENGINEERING")
    ask("Deploy frequency (1=rare, 5=multiple/day)", "deploy_freq")
    ask("Change failure rate (%)", "change_failure_rate")
    ask("MTTR (hours)", "mttr_hours")
    ask("Tech debt % of sprint", "tech_debt_pct")

    print("\n👥 PEOPLE")
    ask("Regrettable attrition (%/yr)", "attrition")
    ask("eNPS score", "enps")
    ask("Time-to-fill (days)", "ttf_days")

    print("\n🔄 OPERATIONS")
    ask("OKR completion rate (%)", "okr_completion")

    print("\n🔒 SECURITY")
    ask("MFA coverage (%)", "mfa_coverage")
    ask("Security training completion (%)", "training_completion")

    return data

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_scorer_base import *  # noqa: F403,E402
# fmt: off
from health_scorer_p1 import Dimension, Metric, Stage, Trend  # noqa: E402,E501
# fmt: on


def build_financial_dimension(stage: Stage, **kwargs) -> Dimension:
    # Thresholds vary by stage
    runway_green = {Stage.SEED: 18, Stage.SERIES_A: 12, Stage.SERIES_B: 12, Stage.SERIES_C: 18}
    runway_red = {Stage.SEED: 9, Stage.SERIES_A: 6, Stage.SERIES_B: 6, Stage.SERIES_C: 9}
    burn_green = {Stage.SEED: 3.0, Stage.SERIES_A: 2.0, Stage.SERIES_B: 1.5, Stage.SERIES_C: 1.0}
    burn_red = {Stage.SEED: 5.0, Stage.SERIES_A: 3.0, Stage.SERIES_B: 2.5, Stage.SERIES_C: 1.5}

    return Dimension(
        key="financial",
        name="Financial Health",
        owner="CFO",
        emoji="💰",
        metrics=[
            Metric("Runway (months)", kwargs.get("runway"),
                   "months", runway_green[stage], runway_red[stage]),
            Metric("Burn multiple", kwargs.get("burn_multiple"),
                   "x", burn_green[stage], burn_red[stage], higher_is_better=False),
            Metric("Gross margin (%)", kwargs.get("gross_margin"),
                   "%", 70, 55),
            Metric("MoM growth (%)", kwargs.get("mom_growth"),
                   "%", 10, 4),
            Metric("Revenue concentration (%)", kwargs.get("revenue_concentration"),
                   "%", 15, 30, higher_is_better=False),
        ],
        trend=kwargs.get("financial_trend", Trend.UNKNOWN),
    )
def build_revenue_dimension(stage: Stage, **kwargs) -> Dimension:
    nrr_green = {Stage.SEED: 100, Stage.SERIES_A: 110, Stage.SERIES_B: 115, Stage.SERIES_C: 120}
    nrr_red = {Stage.SEED: 90, Stage.SERIES_A: 100, Stage.SERIES_B: 105, Stage.SERIES_C: 110}

    return Dimension(
        key="revenue",
        name="Revenue Health",
        owner="CRO",
        emoji="📈",
        metrics=[
            Metric("NRR (%)", kwargs.get("nrr"),
                   "%", nrr_green[stage], nrr_red[stage]),
            Metric("Logo churn (%/yr)", kwargs.get("logo_churn"),
                   "%/yr", 5, 15, higher_is_better=False),
            Metric("Pipeline coverage", kwargs.get("pipeline_coverage"),
                   "x", 3.0, 1.5),
            Metric("CAC payback (months)", kwargs.get("cac_payback"),
                   "months", 12, 24, higher_is_better=False),
            Metric("Win rate (%)", kwargs.get("win_rate"),
                   "%", 25, 15),
        ],
        trend=kwargs.get("revenue_trend", Trend.UNKNOWN),
    )
def build_product_dimension(**kwargs) -> Dimension:
    return Dimension(
        key="product",
        name="Product Health",
        owner="CPO",
        emoji="🚀",
        metrics=[
            Metric("NPS", kwargs.get("nps"), "score", 40, 20),
            Metric("DAU/MAU (%)", kwargs.get("dau_mau"), "%", 35, 15),
            Metric("Core feature adoption (%)", kwargs.get("feature_adoption"), "%", 60, 30),
            Metric("CSAT", kwargs.get("csat"), "/5", 4.2, 3.5),
            Metric("Time-to-value (days)", kwargs.get("ttv_days"), "days", 3, 14, higher_is_better=False),
        ],
        trend=kwargs.get("product_trend", Trend.UNKNOWN),
    )
def build_engineering_dimension(**kwargs) -> Dimension:
    # Deploy frequency encoded: 5=multiple/day, 4=daily, 3=weekly, 2=monthly, 1=<monthly
    return Dimension(
        key="engineering",
        name="Engineering Health",
        owner="CTO",
        emoji="⚙️",
        metrics=[
            Metric("Deploy frequency (1-5)", kwargs.get("deploy_freq"), "scale", 4, 2),
            Metric("Change failure rate (%)", kwargs.get("change_failure_rate"), "%", 5, 15, higher_is_better=False),
            Metric("MTTR (hours)", kwargs.get("mttr_hours"), "hours", 1, 4, higher_is_better=False),
            Metric("Tech debt ratio (%)", kwargs.get("tech_debt_pct"), "%", 15, 35, higher_is_better=False),
            Metric("P0/P1 incidents/month", kwargs.get("incidents_monthly"), "count", 1, 5, higher_is_better=False),
        ],
        trend=kwargs.get("engineering_trend", Trend.UNKNOWN),
    )
def build_people_dimension(stage: Stage, **kwargs) -> Dimension:
    attrition_green = {Stage.SEED: 15, Stage.SERIES_A: 12, Stage.SERIES_B: 10, Stage.SERIES_C: 8}
    attrition_red = {Stage.SEED: 25, Stage.SERIES_A: 18, Stage.SERIES_B: 15, Stage.SERIES_C: 12}

    return Dimension(
        key="people",
        name="People Health",
        owner="CHRO",
        emoji="👥",
        metrics=[
            Metric("Regrettable attrition (%/yr)", kwargs.get("attrition"),
                   "%/yr", attrition_green[stage], attrition_red[stage], higher_is_better=False),
            Metric("eNPS", kwargs.get("enps"), "score", 30, 0),
            Metric("Time-to-fill (days)", kwargs.get("ttf_days"), "days", 45, 90, higher_is_better=False),
            Metric("Internal promotion rate (%)", kwargs.get("internal_promo_rate"), "%", 25, 10),
        ],
        trend=kwargs.get("people_trend", Trend.UNKNOWN),
    )
def build_operations_dimension(**kwargs) -> Dimension:
    return Dimension(
        key="operations",
        name="Operational Health",
        owner="COO",
        emoji="🔄",
        metrics=[
            Metric("OKR completion rate (%)", kwargs.get("okr_completion"), "%", 70, 50),
            Metric("Decision cycle time (hours)", kwargs.get("decision_hours"), "hours", 48, 168, higher_is_better=False),
            Metric("Process maturity (1-5)", kwargs.get("process_maturity"), "level", 3, 1.5),
            Metric("Cross-functional delivery (%)", kwargs.get("xfn_delivery_rate"), "%", 70, 50),
        ],
        trend=kwargs.get("ops_trend", Trend.UNKNOWN),
    )
def build_security_dimension(**kwargs) -> Dimension:
    return Dimension(
        key="security",
        name="Security Health",
        owner="CISO",
        emoji="🔒",
        metrics=[
            Metric("Security incidents (90 days)", kwargs.get("incidents_90d"), "count", 0, 1, higher_is_better=False),
            Metric("MFA coverage (%)", kwargs.get("mfa_coverage"), "%", 95, 80),
            Metric("Security training completion (%)", kwargs.get("training_completion"), "%", 95, 80),
            Metric("Critical CVE patch rate (%)", kwargs.get("cve_patch_rate"), "%", 100, 85),
            Metric("Pen test recency (months)", kwargs.get("pentest_months"), "months", 12, 24, higher_is_better=False),
        ],
        trend=kwargs.get("security_trend", Trend.UNKNOWN),
    )

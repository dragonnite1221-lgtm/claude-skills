# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scenario_modeler_base import *  # noqa: F403,E402
# fmt: off
from scenario_modeler_p1 import CascadeEffect, Domain, Hedge, Scenario, Variable  # noqa: E402,E501
# fmt: on


def build_sample_scenario() -> Scenario:
    """Sample: Customer churn + fundraise miss compound scenario."""
    variables = [
        Variable(
            name="Top customer churn",
            description="Largest customer (28% of ARR) gives 60-day termination notice",
            probability=0.15,
            arrt_impact_pct=28.0,
            runway_impact_months=4.0,
            affected_domains=[
                Domain.FINANCIAL, Domain.REVENUE, Domain.OPERATIONS
            ],
            timeline_days=60,
        ),
        Variable(
            name="Series A delayed 6 months",
            description="Fundraise process extends beyond target close; bridge required",
            probability=0.25,
            arrt_impact_pct=0.0,         # No ARR impact directly
            runway_impact_months=3.0,     # Bridge terms reduce effective runway
            affected_domains=[
                Domain.FINANCIAL, Domain.PEOPLE, Domain.OPERATIONS
            ],
            timeline_days=120,
        ),
        Variable(
            name="Lead engineer resigns",
            description="Engineering lead + 1 senior resign during uncertainty",
            probability=0.20,
            arrt_impact_pct=5.0,          # Roadmap slip causes some revenue impact
            runway_impact_months=1.0,
            affected_domains=[
                Domain.ENGINEERING, Domain.PRODUCT, Domain.REVENUE
            ],
            timeline_days=30,
        ),
    ]

    cascades = [
        CascadeEffect(
            trigger_domain=Domain.REVENUE,
            caused_domain=Domain.FINANCIAL,
            mechanism="ARR loss increases burn multiple; runway compresses",
            severity_multiplier=1.3,
        ),
        CascadeEffect(
            trigger_domain=Domain.FINANCIAL,
            caused_domain=Domain.PEOPLE,
            mechanism="Hiring freeze + uncertainty triggers attrition risk",
            severity_multiplier=1.2,
        ),
        CascadeEffect(
            trigger_domain=Domain.PEOPLE,
            caused_domain=Domain.PRODUCT,
            mechanism="Engineering attrition slips roadmap; customer value drops",
            severity_multiplier=1.15,
        ),
    ]

    hedges = [
        Hedge(
            action="Establish $750K revolving credit line",
            cost_usd=7_500,
            impact_description="Buys 4+ months if churn hits before fundraise closes",
            owner="CFO",
            deadline_days=45,
            reduces_probability=0.40,
        ),
        Hedge(
            action="12-month retention bonuses for 3 key engineers",
            cost_usd=90_000,
            impact_description="Locks critical talent through fundraise uncertainty",
            owner="CHRO",
            deadline_days=30,
            reduces_probability=0.60,
        ),
        Hedge(
            action="Diversify revenue: reduce top customer to <20% ARR in 2 quarters",
            cost_usd=0,
            impact_description="Structural risk reduction; takes 6+ months to achieve",
            owner="CRO",
            deadline_days=14,
            reduces_probability=0.30,
        ),
        Hedge(
            action="Accelerate fundraise: start parallel process, compress timeline",
            cost_usd=15_000,
            impact_description="Closes before scenarios compound; reduces bridge risk",
            owner="CEO",
            deadline_days=7,
            reduces_probability=0.35,
        ),
    ]

    return Scenario(
        name="Customer Churn + Fundraise Miss + Eng Attrition",
        variables=variables,
        cascades=cascades,
        hedges=hedges,
        current_arr_usd=2_000_000,
        current_runway_months=14,
        monthly_burn_usd=140_000,
    )

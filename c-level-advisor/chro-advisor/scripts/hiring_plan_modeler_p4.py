# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_plan_modeler_base import *  # noqa: F403,E402
# fmt: off
from hiring_plan_modeler_p1 import HireTarget, HiringPlan  # noqa: E402,E501
# fmt: on


def build_sample_plan() -> HiringPlan:
    """Sample Series A → B hiring plan."""
    plan = HiringPlan(
        company="AcmeTech (Series A)",
        plan_period="2025 Annual",
        current_headcount=32,
        current_revenue=3_500_000,
        target_revenue=8_000_000,
        overhead_rate=0.25,
        internal_recruiter_cost=140_000,
    )

    plan.hires = [
        # Q1 — Foundation hires
        HireTarget(
            role="Staff Software Engineer (Backend)",
            level="L4", function="Engineering", quarter="Q1-2025",
            base_salary=185_000, bonus_pct=0.0, equity_annual_usd=25_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="High", open_to_internal=True,
            business_case="Core API team is bottleneck for 3 roadmap items. Staff-level needed to lead architecture."
        ),
        HireTarget(
            role="Account Executive (Mid-Market)",
            level="L3", function="Sales", quarter="Q1-2025",
            base_salary=95_000, bonus_pct=0.50, equity_annual_usd=10_000,
            benefits_annual=15_000, recruiter_fee_pct=0.18, ramp_months=4,
            priority="High",
            business_case="Pipeline coverage at 1.8x quota. Need 2.5x by Q2. AE adds $600K ARR/year at ramp."
        ),
        HireTarget(
            role="Product Designer (Senior)",
            level="L3", function="Product", quarter="Q1-2025",
            base_salary=145_000, bonus_pct=0.0, equity_annual_usd=18_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="High",
            business_case="Single designer for 4 squads. UX debt slowing enterprise deals requiring onboarding improvements."
        ),

        # Q2 — Growth hires
        HireTarget(
            role="Engineering Manager (Frontend)",
            level="M1", function="Engineering", quarter="Q2-2025",
            base_salary=175_000, bonus_pct=0.10, equity_annual_usd=22_000,
            benefits_annual=18_000, recruiter_fee_pct=0.20, ramp_months=3,
            priority="High",
            business_case="Frontend team at 7 ICs with no dedicated EM. Performance review debt is high; manager needed."
        ),
        HireTarget(
            role="Account Executive (Mid-Market)",
            level="L2", function="Sales", quarter="Q2-2025",
            base_salary=85_000, bonus_pct=0.50, equity_annual_usd=8_000,
            benefits_annual=15_000, recruiter_fee_pct=0.18, ramp_months=4,
            priority="High",
            business_case="Second AE to reach 2.5x pipeline coverage target."
        ),
        HireTarget(
            role="Customer Success Manager",
            level="L2", function="Customer Success", quarter="Q2-2025",
            base_salary=90_000, bonus_pct=0.15, equity_annual_usd=8_000,
            benefits_annual=15_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="Medium",
            business_case="CSM:account ratio at 1:60, industry standard 1:30. NRR has dipped 4pts in 2 quarters."
        ),
        HireTarget(
            role="Data Engineer",
            level="L2", function="Engineering", quarter="Q2-2025",
            base_salary=155_000, bonus_pct=0.0, equity_annual_usd=18_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=3,
            priority="Medium",
            business_case="Analytics infrastructure blocking product analytics, customer dashboards, and board metrics."
        ),

        # Q3 — Scale hires
        HireTarget(
            role="Senior Software Engineer (Backend)",
            level="L3", function="Engineering", quarter="Q3-2025",
            base_salary=165_000, bonus_pct=0.0, equity_annual_usd=20_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="High",
            business_case="Backend team needs capacity to deliver Q3 roadmap without delaying Q4 items."
        ),
        HireTarget(
            role="Head of Marketing",
            level="M3", function="Marketing", quarter="Q3-2025",
            base_salary=180_000, bonus_pct=0.15, equity_annual_usd=30_000,
            benefits_annual=18_000, recruiter_fee_pct=0.20, ramp_months=3,
            priority="High",
            business_case="No marketing function. 100% of pipeline is outbound. Need inbound by Q1-2026 for Series B."
        ),
        HireTarget(
            role="People Operations Manager",
            level="M1", function="G&A", quarter="Q3-2025",
            base_salary=120_000, bonus_pct=0.10, equity_annual_usd=12_000,
            benefits_annual=16_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="Medium",
            business_case="Founders spending 8hrs/week on HR ops at 40 employees. Unscalable. First dedicated HR hire."
        ),

        # Q4 — Stretch hires (conditional on revenue milestone)
        HireTarget(
            role="Senior Software Engineer (Frontend)",
            level="L3", function="Engineering", quarter="Q4-2025",
            base_salary=160_000, bonus_pct=0.0, equity_annual_usd=18_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=2,
            priority="Medium",
            business_case="Conditional on Q3 ARR exceeding $5.5M. Frontend team capacity planning for 2026 roadmap."
        ),
        HireTarget(
            role="Account Executive (Enterprise)",
            level="L4", function="Sales", quarter="Q4-2025",
            base_salary=120_000, bonus_pct=0.60, equity_annual_usd=15_000,
            benefits_annual=15_000, recruiter_fee_pct=0.20, ramp_months=6,
            priority="Low",
            business_case="Enterprise motion exploratory. Requires ICP validation in Q2-Q3 before committing."
        ),
        HireTarget(
            role="DevOps / Platform Engineer",
            level="L3", function="Engineering", quarter="Q4-2025",
            base_salary=150_000, bonus_pct=0.0, equity_annual_usd=18_000,
            benefits_annual=18_000, recruiter_fee_pct=0.0, ramp_months=3,
            priority="Low",
            business_case="Platform reliability becoming bottleneck. Conditional on uptime SLA breaches continuing in Q3."
        ),
    ]

    return plan

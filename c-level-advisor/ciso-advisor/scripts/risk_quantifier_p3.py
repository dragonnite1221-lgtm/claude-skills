# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402
# fmt: off
from risk_quantifier_p1 import build_risk  # noqa: E402,E501
from risk_quantifier_p2 import _csd_0  # noqa: E402,E501
# fmt: on


def load_sample_risks() -> list[dict]:
    risks = _csd_0()

    risks.append(build_risk(
        name="Credential Stuffing — Customer Accounts",
        category="Application Vulnerability",
        description=(
            "Attackers use leaked credential lists to compromise customer accounts. "
            "Account takeover leads to data theft, fraudulent transactions, and support burden. "
            "16 billion credentials available on darknet as of 2024."
        ),
        asset_value=1_200_000,
        exposure_factor=0.12,
        annual_rate=0.40,
        mitigation_cost=15_000,  # MFA + rate limiting + bot detection
        mitigation_effectiveness=0.95,
        mitigation_status="In Progress",
        business_impacts={
            "Customer Churn": 80_000,
            "Revenue Loss": 45_000,
            "Recovery / Remediation Cost": 19_000,
            "Reputational Damage": 30_000,
        },
        notes="MFA available but optional. Enforcing MFA cuts this risk by ~99%.",
    ))

    risks.append(build_risk(
        name="Phishing — Employee Credential Compromise",
        category="Social Engineering",
        description=(
            "Employee clicks phishing link, surrenders credentials. Without MFA, "
            "this provides full access to email, SaaS apps, and potentially production. "
            "Phishing is the #1 attack vector in the Verizon DBIR."
        ),
        asset_value=1_500_000,
        exposure_factor=0.15,
        annual_rate=0.35,
        mitigation_cost=25_000,  # MFA + security awareness training + email security
        mitigation_effectiveness=0.92,
        mitigation_status="In Progress",
        business_impacts={
            "Business Interruption": 65_000,
            "Customer Churn": 55_000,
            "Recovery / Remediation Cost": 45_000,
            "Reputational Damage": 60_000,
        },
        notes="Primary vector for ransomware and BEC. MFA is the single highest-ROI control.",
    ))

    risks.append(build_risk(
        name="Application API Vulnerability",
        category="Application Vulnerability",
        description=(
            "Unauthenticated or improperly authorized API endpoint exposes customer data "
            "or administrative functions. OWASP API Security Top 10 — broken object-level "
            "authorization is the most common API vulnerability."
        ),
        asset_value=2_000_000,
        exposure_factor=0.18,
        annual_rate=0.15,
        mitigation_cost=30_000,  # DAST + API gateway + code review
        mitigation_effectiveness=0.75,
        mitigation_status="Planned",
        business_impacts={
            "Regulatory Fine": 70_000,
            "Customer Churn": 90_000,
            "Reputational Damage": 100_000,
            "Legal / Litigation": 60_000,
        },
        notes="Need automated API security testing in CI/CD pipeline.",
    ))

    risks.append(build_risk(
        name="DDoS Attack — Production Service",
        category="DDoS / Availability",
        description=(
            "Distributed denial-of-service attack renders production service unavailable. "
            "Average DDoS duration: 4–8 hours. Enterprise SLA breach triggers contractual "
            "penalties. Increasingly used as extortion or distraction tactic."
        ),
        asset_value=1_000_000,
        exposure_factor=0.10,
        annual_rate=0.25,
        mitigation_cost=15_000,  # CDN with DDoS protection (Cloudflare, AWS Shield)
        mitigation_effectiveness=0.85,
        mitigation_status="Mitigated",
        business_impacts={
            "Business Interruption": 45_000,
            "Customer Churn": 30_000,
            "Revenue Loss": 25_000,
        },
        notes="Cloudflare deployed. Residual risk from very large volumetric attacks.",
    ))

    return risks
def calculate_portfolio_summary(risks: list[dict]) -> dict:
    """Aggregate portfolio-level metrics."""
    total_inherent_ale = sum(r["ale"] for r in risks)
    total_mitigated_ale = sum(r["mitigated_ale"] for r in risks)
    total_mitigation_cost = sum(r["mitigation_cost"] for r in risks)
    risk_reduction = total_inherent_ale - total_mitigated_ale
    portfolio_roi = ((risk_reduction - total_mitigation_cost) / total_mitigation_cost * 100
                     if total_mitigation_cost > 0 else 0)

    by_category = {}
    for r in risks:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total_ale": 0.0}
        by_category[cat]["count"] += 1
        by_category[cat]["total_ale"] += r["ale"]

    by_status = {}
    for r in risks:
        status = r["mitigation_status"]
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "total_risks": len(risks),
        "total_inherent_ale": total_inherent_ale,
        "total_mitigated_ale": total_mitigated_ale,
        "total_risk_reduction": risk_reduction,
        "total_mitigation_cost": total_mitigation_cost,
        "portfolio_roi_pct": portfolio_roi,
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1]["total_ale"])),
        "by_mitigation_status": by_status,
    }

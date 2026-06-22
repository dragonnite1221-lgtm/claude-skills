# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402


FRAMEWORKS = {
    "soc2": {
        "name": "SOC 2 Type II",
        "full_name": "AICPA Trust Service Criteria — Security",
        "typical_timeline_months": 12,
        "typical_cost_usd": 65_000,    # Audit + platform
        "annual_maintenance_usd": 40_000,
        "business_value": "Enterprise sales unblock, US market table stakes",
        "mandatory_for": ["B2B SaaS selling to enterprise US companies"],
    },
    "iso27001": {
        "name": "ISO 27001:2022",
        "full_name": "Information Security Management System",
        "typical_timeline_months": 15,
        "typical_cost_usd": 95_000,
        "annual_maintenance_usd": 30_000,
        "business_value": "EU enterprise sales, global credibility",
        "mandatory_for": ["EU enterprise customers", "Government contracts"],
    },
    "hipaa": {
        "name": "HIPAA",
        "full_name": "Health Insurance Portability and Accountability Act",
        "typical_timeline_months": 7,
        "typical_cost_usd": 75_000,
        "annual_maintenance_usd": 20_000,
        "business_value": "Healthcare customer access, BAA execution",
        "mandatory_for": ["Business Associates", "Companies handling PHI"],
    },
    "gdpr": {
        "name": "GDPR",
        "full_name": "General Data Protection Regulation (EU) 2016/679",
        "typical_timeline_months": 5,
        "typical_cost_usd": 45_000,
        "annual_maintenance_usd": 15_000,
        "business_value": "EU market access, legal compliance",
        "mandatory_for": ["EU-based companies", "Any company with EU user data"],
    },
}
def build_control_domain(
    domain_id: str,
    name: str,
    description: str,
    soc2_ref: Optional[str],
    iso27001_ref: Optional[str],
    hipaa_ref: Optional[str],
    gdpr_ref: Optional[str],
    effort_days: int,              # Estimated implementation effort in person-days
    cost_usd: int,                 # Estimated implementation cost (tooling + time)
    implementation_notes: str,
    status: str = "Not Started",   # Not Started | In Progress | Implemented | Verified
    owner: Optional[str] = None,
    target_date: Optional[str] = None,
) -> dict:
    """Build a control domain record."""
    frameworks_applicable = []
    if soc2_ref:
        frameworks_applicable.append("soc2")
    if iso27001_ref:
        frameworks_applicable.append("iso27001")
    if hipaa_ref:
        frameworks_applicable.append("hipaa")
    if gdpr_ref:
        frameworks_applicable.append("gdpr")

    return {
        "domain_id": domain_id,
        "name": name,
        "description": description,
        "references": {
            "soc2": soc2_ref,
            "iso27001": iso27001_ref,
            "hipaa": hipaa_ref,
            "gdpr": gdpr_ref,
        },
        "frameworks_applicable": frameworks_applicable,
        "framework_count": len(frameworks_applicable),
        "effort_days": effort_days,
        "cost_usd": cost_usd,
        "implementation_notes": implementation_notes,
        "status": status,
        "owner": owner,
        "target_date": target_date,
    }

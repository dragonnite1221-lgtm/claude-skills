# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import build_control_domain  # noqa: E402,E501
from compliance_tracker_p2 import _csd_0  # noqa: E402,E501
# fmt: on


def _csd_1():
    controls = _csd_0()

    controls.append(build_control_domain(
        domain_id="RISK-001",
        name="Risk Assessment and Treatment",
        description=(
            "Formal risk assessment methodology. Risk register maintained. "
            "Risk treatment decisions documented. Annual risk review cycle."
        ),
        soc2_ref="CC3.1, CC3.2, CC3.3, CC3.4",
        iso27001_ref="Clause 6.1.2, 6.1.3",
        hipaa_ref="§164.308(a)(1) Security Risk Analysis",
        gdpr_ref="Art. 32, Art. 35 DPIA",
        effort_days=15,
        cost_usd=12_000,
        implementation_notes=(
            "Document risk methodology (FAIR, NIST, ISO 27005). Maintain risk register. "
            "HIPAA: formal security risk analysis required — not optional. "
            "GDPR: DPIA required for high-risk processing activities. Annual refresh."
        ),
        status="Not Started",
        owner="CISO",
    ))

    controls.append(build_control_domain(
        domain_id="TRAIN-001",
        name="Security Awareness Training",
        description=(
            "Annual security awareness training for all employees. "
            "Role-specific training for high-risk roles. Phishing simulations. "
            "Training completion tracking."
        ),
        soc2_ref="CC1.4",
        iso27001_ref="A.6.3, A.6.8",
        hipaa_ref="§164.308(a)(5)",
        gdpr_ref="Art. 39(1)(b)",
        effort_days=5,
        cost_usd=8_000,
        implementation_notes=(
            "Deploy security training platform (KnowBe4, Proofpoint, etc.). "
            "Annual training required — track completion (100% target). "
            "Quarterly phishing simulations. Role-specific training for devs (secure coding), "
            "finance (BEC), support (social engineering)."
        ),
        status="Not Started",
        owner="HR/Security",
    ))

    controls.append(build_control_domain(
        domain_id="CHGMGMT-001",
        name="Change Management",
        description=(
            "Formal change management process for production changes. "
            "Code review requirements. Deployment approvals. Rollback procedures. "
            "Change log maintained."
        ),
        soc2_ref="CC8.1",
        iso27001_ref="A.8.32",
        hipaa_ref="§164.312(c)(1) Integrity controls",
        gdpr_ref="Art. 25 Privacy by design",
        effort_days=10,
        cost_usd=5_000,
        implementation_notes=(
            "Document change management policy. Require peer review for all production changes. "
            "Maintain audit trail in version control. No direct production access — "
            "all changes via CI/CD pipeline."
        ),
        status="In Progress",
        owner="Engineering",
    ))

    controls.append(build_control_domain(
        domain_id="BCP-001",
        name="Business Continuity and Disaster Recovery",
        description=(
            "Business continuity plan. Disaster recovery plan with defined RTO/RPO. "
            "Backup procedures with tested restores. Failover capabilities."
        ),
        soc2_ref="A1.1, A1.2, A1.3",
        iso27001_ref="A.5.29, A.5.30",
        hipaa_ref="§164.308(a)(7) Contingency Plan",
        gdpr_ref="Art. 32(1)(c)",
        effort_days=12,
        cost_usd=15_000,
        implementation_notes=(
            "Define RTO (<4 hours) and RPO (<1 hour) targets. Configure automated backups. "
            "Test restore quarterly — paper backups that aren't tested aren't backups. "
            "Document DR runbook. Annual DR exercise."
        ),
        status="In Progress",
        owner="DevOps",
    ))

    controls.append(build_control_domain(
        domain_id="ASSET-001",
        name="Asset Inventory and Classification",
        description=(
            "Complete inventory of hardware, software, and data assets. "
            "Data classification scheme. Ownership assigned to all assets. "
            "Regular reconciliation."
        ),
        soc2_ref="CC6.1",
        iso27001_ref="A.5.9, A.5.10, A.5.11, A.5.12, A.5.13",
        hipaa_ref="§164.310(d) Device and Media Controls",
        gdpr_ref="Art. 30 Records of Processing Activities",
        effort_days=8,
        cost_usd=5_000,
        implementation_notes=(
            "Build asset register (CMDB or spreadsheet at minimum). "
            "Classify data: Public, Internal, Confidential, Restricted. "
            "GDPR requires RoPA (Record of Processing Activities) — data map of all PII. "
            "ISO 27001 requires SoA referencing asset inventory."
        ),
        status="Not Started",
        owner="IT/Security",
    ))

    controls.append(build_control_domain(
        domain_id="ENDPOINT-001",
        name="Endpoint Security",
        description=(
            "EDR/antivirus on all managed endpoints. Device management (MDM). "
            "Full disk encryption. Patch management. BYOD policy."
        ),
        soc2_ref="CC6.8",
        iso27001_ref="A.8.1, A.8.7",
        hipaa_ref="§164.310(a)(2)(iv) Workstation security",
        gdpr_ref="Art. 32(1)(a)",
        effort_days=8,
        cost_usd=20_000,
        implementation_notes=(
            "Deploy EDR (CrowdStrike, SentinelOne, or Microsoft Defender for Business). "
            "Enable full disk encryption (FileVault/BitLocker). "
            "MDM for device management. BYOD policy documented."
        ),
        status="In Progress",
        owner="IT",
    ))
    return controls

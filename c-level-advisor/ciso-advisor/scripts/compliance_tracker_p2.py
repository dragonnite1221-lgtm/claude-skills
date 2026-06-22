# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import build_control_domain  # noqa: E402,E501
# fmt: on


def _csd_0():
    """
    Core control domains mapped across SOC 2, ISO 27001, HIPAA, and GDPR.
    Each domain represents a logical grouping of controls.
    """
    controls = []

    controls.append(build_control_domain(
        domain_id="IAM-001",
        name="Identity and Access Management",
        description=(
            "Unique user identities, MFA enforcement, SSO, least privilege access, "
            "role-based access control, access provisioning and de-provisioning workflows."
        ),
        soc2_ref="CC6.1, CC6.2, CC6.3",
        iso27001_ref="A.5.15, A.5.16, A.5.17, A.5.18",
        hipaa_ref="§164.312(a)(2)(i), §164.308(a)(3)",
        gdpr_ref="Art. 32(1)(b)",
        effort_days=15,
        cost_usd=25_000,  # SSO + MFA tooling
        implementation_notes=(
            "Deploy IdP (Okta/Azure AD/Google Workspace). Enforce MFA on all applications. "
            "Document access provisioning process. Implement quarterly access reviews."
        ),
        status="In Progress",
        owner="IT/Security",
    ))

    controls.append(build_control_domain(
        domain_id="ENC-001",
        name="Encryption at Rest and in Transit",
        description=(
            "Encryption of sensitive data stored in databases, file systems, and backups. "
            "TLS 1.2+ for all data in transit. Key management and rotation."
        ),
        soc2_ref="CC6.7",
        iso27001_ref="A.8.24",
        hipaa_ref="§164.312(a)(2)(iv), §164.312(e)(2)(ii)",
        gdpr_ref="Art. 32(1)(a)",
        effort_days=10,
        cost_usd=8_000,
        implementation_notes=(
            "Enable encryption at rest on all databases (RDS, S3, etc.). "
            "Configure TLS on all services. Use KMS for key management. "
            "Document encryption standards in a security policy."
        ),
        status="Implemented",
        owner="Engineering",
    ))

    controls.append(build_control_domain(
        domain_id="LOG-001",
        name="Audit Logging and Monitoring",
        description=(
            "Comprehensive logging of user activity, system events, and security events. "
            "Log integrity protection. SIEM or log aggregation. Alerting on anomalies."
        ),
        soc2_ref="CC7.2, CC7.3",
        iso27001_ref="A.8.15, A.8.16, A.8.17",
        hipaa_ref="§164.312(b)",
        gdpr_ref="Art. 32(1)(b)",
        effort_days=20,
        cost_usd=30_000,  # SIEM tooling
        implementation_notes=(
            "Centralize logs from application, infrastructure, and cloud provider. "
            "Define log retention (minimum 1 year). Set up alerting for authentication "
            "failures, privilege escalation, data export events."
        ),
        status="Not Started",
        owner="DevOps/Security",
    ))

    controls.append(build_control_domain(
        domain_id="IR-001",
        name="Incident Response",
        description=(
            "Documented incident response plan. Defined severity levels. Escalation procedures. "
            "Communication templates. Annual tabletop exercise. Post-incident review process."
        ),
        soc2_ref="CC7.3, CC7.4, CC7.5",
        iso27001_ref="A.5.24, A.5.25, A.5.26, A.5.27, A.5.28",
        hipaa_ref="§164.308(a)(6)",
        gdpr_ref="Art. 33, Art. 34",
        effort_days=12,
        cost_usd=10_000,
        implementation_notes=(
            "Write IR plan covering detection, containment, eradication, recovery, communication. "
            "Define breach notification timelines (GDPR: 72 hours, HIPAA: 60 days). "
            "Run annual tabletop exercise. Retain IR firm on retainer."
        ),
        status="In Progress",
        owner="CISO",
    ))

    controls.append(build_control_domain(
        domain_id="VM-001",
        name="Vulnerability Management and Patching",
        description=(
            "Regular vulnerability scanning of infrastructure and applications. "
            "Defined patch SLAs by severity. Penetration testing program. "
            "Dependency vulnerability scanning in CI/CD."
        ),
        soc2_ref="CC7.1",
        iso27001_ref="A.8.8",
        hipaa_ref="§164.308(a)(1)(ii)(A)",
        gdpr_ref="Art. 32(1)(d)",
        effort_days=15,
        cost_usd=20_000,
        implementation_notes=(
            "Deploy infrastructure scanner (Tenable, Qualys, AWS Inspector). "
            "Add SAST/DAST to CI/CD pipeline. Define patch SLAs: Critical <24h, High <7d, "
            "Medium <30d. Conduct annual pentest."
        ),
        status="In Progress",
        owner="DevOps/Security",
    ))

    controls.append(build_control_domain(
        domain_id="VRISK-001",
        name="Vendor and Third-Party Risk Management",
        description=(
            "Inventory of all third-party vendors with data access. Tiered risk assessment "
            "process. Contractual security requirements. Annual reviews for critical vendors."
        ),
        soc2_ref="CC9.2",
        iso27001_ref="A.5.19, A.5.20, A.5.21, A.5.22",
        hipaa_ref="§164.308(b) Business Associate Agreements",
        gdpr_ref="Art. 28 Data Processing Agreements",
        effort_days=10,
        cost_usd=8_000,
        implementation_notes=(
            "Build vendor inventory spreadsheet. Tier vendors (Tier 1: PII access, "
            "Tier 2: business data, Tier 3: no data). Execute DPAs for all processors (GDPR). "
            "Execute BAAs for PHI processors (HIPAA). Annual security questionnaire for Tier 1."
        ),
        status="Not Started",
        owner="Legal/Security",
    ))
    return controls

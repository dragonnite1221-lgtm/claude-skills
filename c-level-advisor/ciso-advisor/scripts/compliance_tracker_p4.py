# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import build_control_domain  # noqa: E402,E501
from compliance_tracker_p3 import _csd_1  # noqa: E402,E501
# fmt: on


def load_control_library() -> list[dict]:
    controls = _csd_1()

    controls.append(build_control_domain(
        domain_id="POLICY-001",
        name="Security Policies and Procedures",
        description=(
            "Documented security policies covering acceptable use, access control, "
            "incident response, data classification, vendor management, etc. "
            "Annual review cycle. Employee attestation."
        ),
        soc2_ref="CC1.2, CC1.3",
        iso27001_ref="A.5.1, A.5.2",
        hipaa_ref="§164.308(a)(1) Security Management Process",
        gdpr_ref="Art. 24 Responsibility of the controller",
        effort_days=15,
        cost_usd=10_000,
        implementation_notes=(
            "Minimum policy set: Information Security Policy, Acceptable Use, "
            "Access Control, Incident Response, Data Classification, Password, "
            "Change Management, Vendor Management, Business Continuity. "
            "Use policy templates from GRC platform (Vanta/Drata)."
        ),
        status="In Progress",
        owner="CISO",
    ))

    controls.append(build_control_domain(
        domain_id="PRIV-001",
        name="Privacy and Data Subject Rights",
        description=(
            "Privacy policy and notices. Data subject rights fulfilment process "
            "(access, erasure, portability). Consent management. Cookie compliance. "
            "Privacy by design in product development."
        ),
        soc2_ref=None,  # Not a SOC 2 requirement (unless Privacy TSC selected)
        iso27001_ref="A.5.34",
        hipaa_ref="§164.524 Access, §164.528 Accounting of Disclosures",
        gdpr_ref="Art. 13, 14, 15–22 (Rights), Art. 25",
        effort_days=20,
        cost_usd=15_000,
        implementation_notes=(
            "GDPR: Update privacy policy, implement DSAR process (30-day SLA), "
            "build deletion capability into product. Cookie consent (PECR/ePrivacy). "
            "HIPAA: Patient rights for PHI access. "
            "Consider OneTrust, Termly, or CookieYes for consent management."
        ),
        status="Not Started",
        owner="Legal/Product",
    ))

    controls.append(build_control_domain(
        domain_id="NET-001",
        name="Network Security and Segmentation",
        description=(
            "Network segmentation (production vs. development vs. corporate). "
            "Firewall rules. Intrusion detection. VPN or ZTNA for remote access."
        ),
        soc2_ref="CC6.6, CC6.7",
        iso27001_ref="A.8.20, A.8.21, A.8.22",
        hipaa_ref="§164.312(e)(1) Transmission security",
        gdpr_ref="Art. 32(1)(a)",
        effort_days=12,
        cost_usd=18_000,
        implementation_notes=(
            "Segment production from development. WAF in front of public applications. "
            "Replace VPN with ZTNA for remote access (Series B+ consideration). "
            "DDoS protection (Cloudflare or AWS Shield)."
        ),
        status="In Progress",
        owner="DevOps",
    ))

    controls.append(build_control_domain(
        domain_id="PENTEST-001",
        name="Penetration Testing",
        description=(
            "Annual external penetration test by qualified third-party firm. "
            "Finding remediation tracking. Results reviewed by leadership."
        ),
        soc2_ref="CC7.1",
        iso27001_ref="A.8.8",
        hipaa_ref="§164.308(a)(8) Evaluation",
        gdpr_ref="Art. 32(1)(d)",
        effort_days=5,
        cost_usd=25_000,
        implementation_notes=(
            "Scope: external attack surface, application, API, and optionally social engineering. "
            "Budget $15–35K for a reputable firm. Track findings in risk register. "
            "Re-test critical findings within 90 days. Share pentest summary with enterprise "
            "customers on request (under NDA)."
        ),
        status="Not Started",
        owner="CISO",
    ))

    return controls

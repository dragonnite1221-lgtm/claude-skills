# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_quantifier_base import *  # noqa: F403,E402
# fmt: off
from risk_quantifier_p1 import build_risk  # noqa: E402,E501
# fmt: on


def _csd_0():
    """
    Sample risk register for a Series B SaaS company with ~$15M ARR,
    ~50K customer records, B2B enterprise focus.
    """
    risks = []

    risks.append(build_risk(
        name="Customer Database Breach",
        category="Data Breach",
        description=(
            "Unauthorized access to production database containing 50K+ customer records "
            "including PII (name, email, company, payment method). Attack vector: SQL injection, "
            "compromised credentials, or insider access."
        ),
        asset_value=5_000_000,   # Value of customer database (revenue impact + regulatory)
        exposure_factor=0.30,    # ~30% of asset value lost in a breach event
        annual_rate=0.12,        # ~12% chance per year (based on Verizon DBIR industry data)
        mitigation_cost=45_000,  # WAF + DAST + DB activity monitoring annual cost
        mitigation_effectiveness=0.80,
        mitigation_status="In Progress",
        business_impacts={
            "Regulatory Fine": 85_000,      # GDPR/CCPA exposure
            "Legal / Litigation": 150_000,  # Class action exposure
            "Customer Churn": 300_000,      # Lost ARR from breach-triggered churn
            "Reputational Damage": 200_000, # Brand impact / deal loss
            "Recovery / Remediation Cost": 65_000,
        },
        notes="SOC 2 Type II controls partially address. Next step: DB activity monitoring.",
    ))

    risks.append(build_risk(
        name="Ransomware Attack",
        category="Ransomware / Extortion",
        description=(
            "Ransomware encrypts production systems. Average ransom demand for a "
            "Series B company is $350K–$800K. Recovery without ransom payment: 2–6 weeks downtime. "
            "Attack vector: phishing email with malicious attachment, RDP exposure."
        ),
        asset_value=3_500_000,
        exposure_factor=0.25,
        annual_rate=0.15,
        mitigation_cost=60_000,  # EDR + email security + backup hardening
        mitigation_effectiveness=0.85,
        mitigation_status="Planned",
        business_impacts={
            "Business Interruption": 450_000,  # 4 weeks downtime × $112K/week revenue
            "Recovery / Remediation Cost": 180_000,
            "Customer Churn": 125_000,
            "Revenue Loss": 75_000,
        },
        notes="Offline, tested backups reduce recovery time and eliminate ransom pressure.",
    ))

    risks.append(build_risk(
        name="Privileged Insider Data Theft",
        category="Insider Threat",
        description=(
            "Disgruntled or financially motivated employee with elevated access exfiltrates "
            "customer data, IP, or trade secrets. Detection is typically slow (median: 197 days "
            "per IBM Cost of Data Breach Report)."
        ),
        asset_value=2_800_000,
        exposure_factor=0.20,
        annual_rate=0.08,
        mitigation_cost=35_000,  # DLP + UEBA + PAM
        mitigation_effectiveness=0.65,
        mitigation_status="None",
        business_impacts={
            "Legal / Litigation": 120_000,
            "Customer Churn": 90_000,
            "Reputational Damage": 75_000,
            "Recovery / Remediation Cost": 40_000,
        },
        notes="No DLP or UEBA currently deployed. Highest detection gap.",
    ))

    risks.append(build_risk(
        name="Critical SaaS Vendor Breach (Supply Chain)",
        category="Third-Party / Supply Chain",
        description=(
            "A critical SaaS vendor (e.g., Salesforce, Slack, AWS, GitHub) suffers a breach "
            "that compromises data entrusted to them or disrupts your operations. You have "
            "limited control but full liability to customers."
        ),
        asset_value=2_200_000,
        exposure_factor=0.15,
        annual_rate=0.18,
        mitigation_cost=20_000,  # Vendor risk assessment program
        mitigation_effectiveness=0.40,  # Limited — you can't control vendor security
        mitigation_status="Planned",
        business_impacts={
            "Business Interruption": 95_000,
            "Customer Churn": 75_000,
            "Reputational Damage": 50_000,
            "Recovery / Remediation Cost": 30_000,
        },
        notes="Third-party risk is partially transferable via contractual SLAs and cyber insurance.",
    ))

    risks.append(build_risk(
        name="Business Email Compromise (BEC)",
        category="Business Email Compromise",
        description=(
            "Attacker impersonates CEO, CFO, or vendor to redirect wire transfers, gift card "
            "purchases, or payroll. Median BEC loss: $125K. FBI IC3 reports BEC as #1 "
            "cybercrime by financial loss."
        ),
        asset_value=500_000,
        exposure_factor=0.40,
        annual_rate=0.30,
        mitigation_cost=12_000,  # Email authentication (DMARC) + training + callback procedures
        mitigation_effectiveness=0.90,
        mitigation_status="In Progress",
        business_impacts={
            "Revenue Loss": 125_000,       # Direct financial theft (often unrecoverable)
            "Recovery / Remediation Cost": 25_000,
            "Legal / Litigation": 15_000,
        },
        notes="DMARC deployed. Need to enforce wire transfer callback procedures.",
    ))

    risks.append(build_risk(
        name="Cloud Misconfiguration — S3 / Storage Exposure",
        category="Cloud Misconfiguration",
        description=(
            "Public exposure of S3 buckets, GCS buckets, or Azure Blob storage containing "
            "sensitive data. One of the most common causes of data breaches. Often undetected "
            "for months. 2023 IBM study: 82% of breaches involved data stored in cloud."
        ),
        asset_value=1_800_000,
        exposure_factor=0.20,
        annual_rate=0.20,
        mitigation_cost=18_000,  # CSPM tool + IaC scanning
        mitigation_effectiveness=0.90,
        mitigation_status="Planned",
        business_impacts={
            "Regulatory Fine": 60_000,
            "Reputational Damage": 120_000,
            "Legal / Litigation": 45_000,
            "Recovery / Remediation Cost": 35_000,
        },
        notes="No CSPM currently. High frequency, high detectability, low mitigation cost.",
    ))
    return risks

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dpia_generator_base import *  # noqa: F403,E402


RISK_CATEGORIES = {
    "unauthorized_access": {
        "description": "Risk of unauthorized access to personal data",
        "impact": "high",
        "mitigations": [
            "Implement access controls and authentication",
            "Use encryption for data at rest and in transit",
            "Maintain audit logs of access",
            "Implement least privilege principle"
        ]
    },
    "data_breach": {
        "description": "Risk of data breach or unauthorized disclosure",
        "impact": "high",
        "mitigations": [
            "Implement intrusion detection systems",
            "Establish incident response procedures",
            "Regular security assessments",
            "Employee security training"
        ]
    },
    "excessive_collection": {
        "description": "Risk of collecting more data than necessary",
        "impact": "medium",
        "mitigations": [
            "Implement data minimization principles",
            "Regular review of data collected",
            "Privacy by design approach",
            "Document purpose for each data element"
        ]
    },
    "purpose_creep": {
        "description": "Risk of using data for purposes beyond original scope",
        "impact": "medium",
        "mitigations": [
            "Clear purpose limitation policies",
            "Consent management for new purposes",
            "Technical controls on data access",
            "Regular purpose review"
        ]
    },
    "retention_violation": {
        "description": "Risk of retaining data longer than necessary",
        "impact": "medium",
        "mitigations": [
            "Implement retention schedules",
            "Automated deletion processes",
            "Regular data inventory audits",
            "Document retention justification"
        ]
    },
    "rights_violation": {
        "description": "Risk of failing to fulfill data subject rights",
        "impact": "high",
        "mitigations": [
            "Implement subject access request process",
            "Technical capability for data portability",
            "Deletion/erasure procedures",
            "Staff training on rights requests"
        ]
    },
    "inaccurate_data": {
        "description": "Risk of processing inaccurate or outdated data",
        "impact": "medium",
        "mitigations": [
            "Data quality checks at collection",
            "Regular data verification",
            "Easy update mechanisms for subjects",
            "Automated accuracy validation"
        ]
    },
    "third_party_risk": {
        "description": "Risk from third-party processors",
        "impact": "high",
        "mitigations": [
            "Due diligence on processors",
            "Data Processing Agreements",
            "Regular processor audits",
            "Clear processor instructions"
        ]
    }
}

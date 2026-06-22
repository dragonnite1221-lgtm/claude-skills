# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hipaa_risk_assessment_base import *  # noqa: F403,E402


HIPAA_SAFEGUARDS = {
    "administrative": {
        "title": "Administrative Safeguards (§164.308)",
        "controls": {
            "security_management": {
                "title": "Security Management Process",
                "requirement": "Risk analysis, risk management, sanction policy",
                "doc_patterns": ["risk_assessment*", "security_policy*", "sanction*"],
                "code_patterns": [],
                "weight": 10
            },
            "security_officer": {
                "title": "Assigned Security Responsibility",
                "requirement": "Designated security official",
                "doc_patterns": ["security_officer*", "hipaa_officer*", "privacy_officer*"],
                "code_patterns": [],
                "weight": 5
            },
            "workforce_security": {
                "title": "Workforce Security",
                "requirement": "Authorization/supervision, clearance, termination procedures",
                "doc_patterns": ["access_control*", "termination*", "hr_security*"],
                "code_patterns": [],
                "weight": 5
            },
            "access_management": {
                "title": "Information Access Management",
                "requirement": "Access authorization, establishment, modification",
                "doc_patterns": ["access_management*", "role_definition*", "access_control*"],
                "code_patterns": [r"role.*based", r"permission", r"authorization"],
                "weight": 8
            },
            "security_training": {
                "title": "Security Awareness and Training",
                "requirement": "Training program, security reminders",
                "doc_patterns": ["training*", "security_awareness*"],
                "code_patterns": [],
                "weight": 5
            },
            "incident_procedures": {
                "title": "Security Incident Procedures",
                "requirement": "Incident response and reporting",
                "doc_patterns": ["incident*", "breach*", "security_event*"],
                "code_patterns": [r"incident.*report", r"security.*alert", r"breach.*notify"],
                "weight": 8
            },
            "contingency_plan": {
                "title": "Contingency Plan",
                "requirement": "Backup, disaster recovery, emergency mode",
                "doc_patterns": ["contingency*", "disaster_recovery*", "backup*", "dr_plan*"],
                "code_patterns": [r"backup", r"recovery", r"failover"],
                "weight": 8
            },
            "evaluation": {
                "title": "Evaluation",
                "requirement": "Periodic security evaluations",
                "doc_patterns": ["security_audit*", "hipaa_audit*", "compliance_review*"],
                "code_patterns": [],
                "weight": 5
            },
            "baa": {
                "title": "Business Associate Contracts",
                "requirement": "Written contracts with business associates",
                "doc_patterns": ["baa*", "business_associate*", "vendor_agreement*"],
                "code_patterns": [],
                "weight": 5
            }
        }
    },
    "physical": {
        "title": "Physical Safeguards (§164.310)",
        "controls": {
            "facility_access": {
                "title": "Facility Access Controls",
                "requirement": "Physical access procedures and controls",
                "doc_patterns": ["facility_access*", "physical_security*", "access_control*"],
                "code_patterns": [],
                "weight": 5
            },
            "workstation_use": {
                "title": "Workstation Use",
                "requirement": "Policies for workstation use and security",
                "doc_patterns": ["workstation*", "endpoint*", "device_policy*"],
                "code_patterns": [],
                "weight": 3
            },
            "device_media": {
                "title": "Device and Media Controls",
                "requirement": "Disposal, media re-use, accountability",
                "doc_patterns": ["media_disposal*", "device_disposal*", "data_sanitization*"],
                "code_patterns": [r"secure.*delete", r"wipe", r"sanitize"],
                "weight": 5
            }
        }
    },
    "technical": {
        "title": "Technical Safeguards (§164.312)",
        "controls": {
            "access_control": {
                "title": "Access Control",
                "requirement": "Unique user ID, emergency access, auto logoff, encryption",
                "doc_patterns": ["access_control*", "authentication*", "session*"],
                "code_patterns": [
                    r"authentication",
                    r"authorize",
                    r"session.*timeout",
                    r"auto.*logout",
                    r"unique.*id",
                    r"user.*id"
                ],
                "weight": 10
            },
            "audit_controls": {
                "title": "Audit Controls",
                "requirement": "Record and examine activity in systems with ePHI",
                "doc_patterns": ["audit_log*", "access_log*", "security_log*"],
                "code_patterns": [
                    r"audit.*log",
                    r"access.*log",
                    r"log.*access",
                    r"security.*event",
                    r"logger"
                ],
                "weight": 10
            },
            "integrity": {
                "title": "Integrity Controls",
                "requirement": "Mechanism to authenticate ePHI",
                "doc_patterns": ["data_integrity*", "checksum*", "hash*"],
                "code_patterns": [
                    r"checksum",
                    r"hash",
                    r"hmac",
                    r"integrity.*check",
                    r"digital.*signature"
                ],
                "weight": 8
            },
            "authentication": {
                "title": "Person or Entity Authentication",
                "requirement": "Verify identity of person or entity seeking access",
                "doc_patterns": ["authentication*", "identity*", "mfa*", "2fa*"],
                "code_patterns": [
                    r"authenticate",
                    r"mfa",
                    r"two.*factor",
                    r"2fa",
                    r"multi.*factor",
                    r"oauth",
                    r"jwt"
                ],
                "weight": 10
            },
            "transmission_security": {
                "title": "Transmission Security",
                "requirement": "Encryption during transmission",
                "doc_patterns": ["encryption*", "tls*", "ssl*", "transport_security*"],
                "code_patterns": [
                    r"https",
                    r"tls",
                    r"ssl",
                    r"encrypt.*transit",
                    r"secure.*connection"
                ],
                "weight": 10
            }
        }
    }
}

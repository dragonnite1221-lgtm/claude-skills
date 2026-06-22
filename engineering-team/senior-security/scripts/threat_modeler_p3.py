# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402
# fmt: off
from threat_modeler_p1 import Threat  # noqa: E402,E501
# fmt: on


def _mod_cg0_1():
    return {
        "api": [
        Threat(
            category="Spoofing",
            name="API Key Impersonation",
            description="Attacker uses stolen or leaked API keys",
            attack_vector="GitHub exposure, client-side storage, logging",
            impact="Unauthorized API access, data theft",
            likelihood=4,
            severity=4,
            mitigations=[
                "Implement API key rotation policies",
                "Use short-lived tokens where possible",
                "Monitor for exposed secrets in repositories",
                "Implement IP allowlisting for API keys"
            ]
        ),
        Threat(
            category="Tampering",
            name="Request Manipulation",
            description="Attacker modifies API requests in transit",
            attack_vector="Man-in-the-middle, proxy interception",
            impact="Data corruption, unauthorized actions",
            likelihood=2,
            severity=4,
            mitigations=[
                "Enforce TLS 1.3 for all connections",
                "Implement request signing (HMAC)",
                "Use certificate pinning for mobile apps",
                "Validate request integrity on server"
            ]
        ),
        Threat(
            category="Information Disclosure",
            name="Excessive Data Exposure",
            description="API returns more data than needed",
            attack_vector="Response inspection, schema analysis",
            impact="Sensitive data leakage",
            likelihood=4,
            severity=3,
            mitigations=[
                "Implement field-level access control",
                "Use GraphQL with depth limiting",
                "Apply response filtering based on role",
                "Audit API responses for sensitive fields"
            ]
        ),
        Threat(
            category="Denial of Service",
            name="API Rate Limit Bypass",
            description="Attacker circumvents rate limiting",
            attack_vector="Distributed requests, header spoofing",
            impact="Service degradation, resource exhaustion",
            likelihood=3,
            severity=3,
            mitigations=[
                "Implement layered rate limiting",
                "Use token bucket or leaky bucket algorithms",
                "Rate limit by user, IP, and API key",
                "Deploy API gateway with DoS protection"
            ]
        )
    ],
        "database": [
        Threat(
            category="Tampering",
            name="SQL Injection",
            description="Attacker injects malicious SQL commands",
            attack_vector="Input fields, URL parameters, headers",
            impact="Data theft, modification, destruction",
            likelihood=3,
            severity=5,
            mitigations=[
                "Use parameterized queries exclusively",
                "Apply input validation and sanitization",
                "Implement least privilege database accounts",
                "Deploy web application firewall (WAF)"
            ]
        ),
        Threat(
            category="Information Disclosure",
            name="Unencrypted Data at Rest",
            description="Sensitive data stored without encryption",
            attack_vector="Physical theft, backup exposure, insider threat",
            impact="Mass data breach",
            likelihood=2,
            severity=5,
            mitigations=[
                "Implement transparent data encryption (TDE)",
                "Use field-level encryption for PII",
                "Encrypt database backups",
                "Manage encryption keys securely"
            ]
        ),
        Threat(
            category="Repudiation",
            name="Audit Log Tampering",
            description="Attacker modifies or deletes database logs",
            attack_vector="SQL injection, admin access, log rotation",
            impact="Cannot prove what actions occurred",
            likelihood=2,
            severity=4,
            mitigations=[
                "Write audit logs to immutable storage",
                "Implement cryptographic log chaining",
                "Use separate audit database with restricted access",
                "Monitor for log gaps and anomalies"
            ]
        )
    ],
    }

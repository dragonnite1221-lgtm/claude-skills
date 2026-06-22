# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402
# fmt: off
from threat_modeler_p1 import Threat  # noqa: E402,E501
# fmt: on


def _mod_cg0_0():
    return {
        "authentication": [
        Threat(
            category="Spoofing",
            name="Credential Theft",
            description="Attacker obtains valid credentials through phishing or theft",
            attack_vector="Phishing emails, keyloggers, credential stuffing",
            impact="Full account compromise, data access",
            likelihood=4,
            severity=5,
            mitigations=[
                "Implement multi-factor authentication (MFA)",
                "Use phishing-resistant authentication (FIDO2/WebAuthn)",
                "Deploy credential monitoring and breach detection",
                "Enforce strong password policies with complexity requirements"
            ]
        ),
        Threat(
            category="Spoofing",
            name="Session Hijacking",
            description="Attacker steals or predicts session tokens",
            attack_vector="XSS, network sniffing, session fixation",
            impact="Unauthorized access to user session",
            likelihood=3,
            severity=4,
            mitigations=[
                "Use secure, HttpOnly, SameSite cookies",
                "Implement session binding (IP, user agent)",
                "Rotate session tokens after authentication",
                "Use short session timeouts for sensitive operations"
            ]
        ),
        Threat(
            category="Tampering",
            name="JWT Token Manipulation",
            description="Attacker modifies JWT claims or signature",
            attack_vector="Algorithm confusion, weak secrets, none algorithm",
            impact="Privilege escalation, identity spoofing",
            likelihood=3,
            severity=5,
            mitigations=[
                "Use asymmetric algorithms (RS256, ES256)",
                "Validate algorithm in code, not from token",
                "Implement proper key management",
                "Add expiration and audience validation"
            ]
        ),
        Threat(
            category="Repudiation",
            name="Authentication Event Denial",
            description="User denies performing authentication actions",
            attack_vector="Claim of compromised credentials",
            impact="Dispute resolution difficulty, fraud",
            likelihood=2,
            severity=3,
            mitigations=[
                "Log all authentication events with timestamps",
                "Capture device fingerprints and IP addresses",
                "Implement tamper-evident audit logs",
                "Use digital signatures for critical actions"
            ]
        ),
        Threat(
            category="Information Disclosure",
            name="Password Hash Exposure",
            description="Password hashes leaked through breach or injection",
            attack_vector="SQL injection, backup exposure, insider threat",
            impact="Mass credential compromise",
            likelihood=2,
            severity=5,
            mitigations=[
                "Use strong password hashing (Argon2id, bcrypt)",
                "Implement database encryption at rest",
                "Apply parameterized queries everywhere",
                "Segment database access by function"
            ]
        ),
        Threat(
            category="Denial of Service",
            name="Authentication Brute Force",
            description="Attacker overwhelms authentication service",
            attack_vector="Distributed credential stuffing, password spraying",
            impact="Service unavailability, account lockouts",
            likelihood=4,
            severity=3,
            mitigations=[
                "Implement progressive rate limiting",
                "Use CAPTCHA after failed attempts",
                "Deploy account lockout with notification",
                "Use distributed denial of service protection"
            ]
        ),
        Threat(
            category="Elevation of Privilege",
            name="Privilege Escalation via Auth Bypass",
            description="Attacker gains admin access through auth flaws",
            attack_vector="IDOR, insecure direct object references, role confusion",
            impact="Full system compromise",
            likelihood=2,
            severity=5,
            mitigations=[
                "Implement server-side authorization checks",
                "Use role-based access control (RBAC)",
                "Validate permissions on every request",
                "Audit privilege changes"
            ]
        )
    ],
    }

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402
# fmt: off
from threat_modeler_p1 import Threat  # noqa: E402,E501
from threat_modeler_p2 import _mod_cg0_0  # noqa: E402,E501
from threat_modeler_p3 import _mod_cg0_1  # noqa: E402,E501
# fmt: on


def _mod_cg0_2():
    return {
        "network": [
        Threat(
            category="Information Disclosure",
            name="Network Traffic Interception",
            description="Attacker captures unencrypted traffic",
            attack_vector="ARP spoofing, rogue access points, packet sniffing",
            impact="Credential theft, data exposure",
            likelihood=2,
            severity=4,
            mitigations=[
                "Enforce TLS everywhere (no HTTP)",
                "Implement HSTS with preloading",
                "Use mutual TLS for service-to-service",
                "Deploy network segmentation"
            ]
        ),
        Threat(
            category="Denial of Service",
            name="DDoS Attack",
            description="Attacker floods network with traffic",
            attack_vector="Volumetric attacks, application layer attacks",
            impact="Complete service unavailability",
            likelihood=3,
            severity=4,
            mitigations=[
                "Deploy CDN with DDoS protection",
                "Implement rate limiting at edge",
                "Use anycast DNS distribution",
                "Have incident response runbook ready"
            ]
        )
    ],
        "storage": [
        Threat(
            category="Information Disclosure",
            name="Insecure File Upload",
            description="Attacker accesses uploaded files",
            attack_vector="Direct URL access, path traversal",
            impact="Data breach, malware distribution",
            likelihood=3,
            severity=4,
            mitigations=[
                "Generate random file names",
                "Store files outside web root",
                "Implement signed URLs with expiration",
                "Scan uploads for malware"
            ]
        ),
        Threat(
            category="Tampering",
            name="File Integrity Violation",
            description="Attacker modifies stored files",
            attack_vector="Write access exploit, supply chain attack",
            impact="Data corruption, code execution",
            likelihood=2,
            severity=4,
            mitigations=[
                "Implement file integrity monitoring",
                "Use cryptographic hashes for verification",
                "Apply immutable storage for critical files",
                "Version control with audit trail"
            ]
        )
    ],
    }
THREAT_DATABASE = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2()}
COMPONENT_MAPPING = {
    "authentication": ["authentication"],
    "login": ["authentication"],
    "auth": ["authentication"],
    "api": ["api"],
    "api gateway": ["api", "network"],
    "rest api": ["api"],
    "graphql": ["api"],
    "database": ["database"],
    "db": ["database"],
    "postgres": ["database"],
    "mysql": ["database"],
    "mongodb": ["database"],
    "network": ["network"],
    "load balancer": ["network"],
    "cdn": ["network"],
    "storage": ["storage"],
    "s3": ["storage"],
    "file upload": ["storage"],
    "user service": ["authentication", "database"],
    "payment": ["api", "database", "authentication"],
    "web application": ["authentication", "api", "database", "network"],
    "microservice": ["api", "network", "authentication"],
}
def get_threats_for_component(component: str) -> List[Threat]:
    """Get applicable threats for a component."""
    component_lower = component.lower()

    # Find matching categories
    categories = []
    for key, value in COMPONENT_MAPPING.items():
        if key in component_lower:
            categories.extend(value)

    # If no specific match, return all threats
    if not categories:
        categories = list(THREAT_DATABASE.keys())

    # Collect unique threats
    threats = []
    seen = set()
    for category in set(categories):
        if category in THREAT_DATABASE:
            for threat in THREAT_DATABASE[category]:
                threat_key = (threat.category, threat.name)
                if threat_key not in seen:
                    threats.append(threat)
                    seen.add(threat_key)

    return sorted(threats, key=lambda t: t.risk_score, reverse=True)

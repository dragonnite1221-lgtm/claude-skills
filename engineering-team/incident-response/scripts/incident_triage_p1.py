# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402


DWELL_CRITICAL = 720    # hours (30 days)
DWELL_HIGH = 168        # hours (7 days)
DWELL_MEDIUM = 24       # hours (1 day)
EVIDENCE_SOURCES = [
    "siem_logs",
    "edr_telemetry",
    "network_pcap",
    "dns_logs",
    "proxy_logs",
    "cloud_trail",
    "authentication_logs",
    "endpoint_filesystem",
    "memory_dump",
    "email_headers",
]
CHAIN_OF_CUSTODY_STEPS = [
    "Identify and preserve volatile evidence (RAM, network connections)",
    "Hash all collected artifacts (SHA-256) before analysis",
    "Document collection timestamp and analyst identity",
    "Transfer artifacts to isolated forensic workstation",
    "Maintain write-blockers for disk images",
    "Log every access to evidence with timestamps",
    "Store originals in secure, access-controlled evidence vault",
    "Maintain dual-custody chain for legal proceedings",
]
INCIDENT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "ransomware": {
        "default_severity": "sev1",
        "mitre": "T1486",
        "response_sla_minutes": 15,
    },
    "data_exfiltration": {
        "default_severity": "sev1",
        "mitre": "T1048",
        "response_sla_minutes": 15,
    },
    "apt_intrusion": {
        "default_severity": "sev1",
        "mitre": "T1190",
        "response_sla_minutes": 15,
    },
    "supply_chain_compromise": {
        "default_severity": "sev1",
        "mitre": "T1195",
        "response_sla_minutes": 15,
    },
    "credential_compromise": {
        "default_severity": "sev2",
        "mitre": "T1078",
        "response_sla_minutes": 60,
    },
    "lateral_movement": {
        "default_severity": "sev2",
        "mitre": "T1021",
        "response_sla_minutes": 60,
    },
    "privilege_escalation": {
        "default_severity": "sev2",
        "mitre": "T1068",
        "response_sla_minutes": 60,
    },
    "malware_detected": {
        "default_severity": "sev2",
        "mitre": "T1204",
        "response_sla_minutes": 60,
    },
    "phishing": {
        "default_severity": "sev3",
        "mitre": "T1566",
        "response_sla_minutes": 240,
    },
    "unauthorized_access": {
        "default_severity": "sev3",
        "mitre": "T1078",
        "response_sla_minutes": 240,
    },
    "policy_violation": {
        "default_severity": "sev4",
        "mitre": "T1530",
        "response_sla_minutes": 1440,
    },
    "vulnerability_discovered": {
        "default_severity": "sev4",
        "mitre": "T1190",
        "response_sla_minutes": 1440,
    },
    "dos_attack": {
        "default_severity": "sev3",
        "mitre": "T1498",
        "response_sla_minutes": 240,
    },
    "insider_threat": {
        "default_severity": "sev2",
        "mitre": "T1078.002",
        "response_sla_minutes": 60,
    },
}

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402
# fmt: off
from incident_triage_p1 import CHAIN_OF_CUSTODY_STEPS, DWELL_CRITICAL, DWELL_HIGH, DWELL_MEDIUM, EVIDENCE_SOURCES  # noqa: E402,E501
# fmt: on


def assess_dwell_severity(dwell_hours: float) -> str:
    """
    Map dwell time (hours) to a severity label.

    Returns 'critical', 'high', 'medium', or 'low'.
    """
    if dwell_hours >= DWELL_CRITICAL:
        return "critical"
    if dwell_hours >= DWELL_HIGH:
        return "high"
    if dwell_hours >= DWELL_MEDIUM:
        return "medium"
    return "low"
def _looks_like_ip(value: str) -> bool:
    """Heuristic: does the string look like an IPv4 address?"""
    import re
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", value.strip()))
def _looks_like_hash(value: str) -> bool:
    """Heuristic: does the string look like a hex hash (MD5/SHA1/SHA256)?"""
    import re
    return bool(re.match(r"^[0-9a-fA-F]{32,64}$", value.strip()))
def _source_applicable(source: str, fields: dict) -> bool:
    """Decide if an evidence source is relevant given parsed fields."""
    mapping = {
        "network_pcap": fields.get("source_ip") not in (None, "unknown"),
        "edr_telemetry": fields.get("hostname") not in (None, "unknown"),
        "authentication_logs": fields.get("user_account") not in (None, "unknown"),
        "dns_logs": fields.get("destination_ip") not in (None, "unknown"),
        "endpoint_filesystem": fields.get("process_name") not in (None, "unknown"),
        "memory_dump": fields.get("process_name") not in (None, "unknown"),
    }
    return mapping.get(source, True)
def build_ioc_summary(fields: dict) -> dict:
    """
    Build a structured IOC summary from parsed forensic fields.

    Returns a dict suitable for embedding in the triage output.
    """
    iocs = fields.get("iocs", [])
    dwell_hours = fields.get("dwell_hours", 0.0)
    dwell_severity = assess_dwell_severity(dwell_hours)

    # Classify IOCs by rough heuristic
    ip_iocs = [i for i in iocs if _looks_like_ip(i)]
    hash_iocs = [i for i in iocs if _looks_like_hash(i)]
    domain_iocs = [i for i in iocs if not _looks_like_ip(i) and not _looks_like_hash(i)]

    return {
        "total_ioc_count": len(iocs),
        "ip_indicators": ip_iocs,
        "hash_indicators": hash_iocs,
        "domain_url_indicators": domain_iocs,
        "dwell_hours": round(dwell_hours, 2),
        "dwell_severity": dwell_severity,
        "evidence_sources_applicable": [
            src for src in EVIDENCE_SOURCES
            if _source_applicable(src, fields)
        ],
        "chain_of_custody_steps": CHAIN_OF_CUSTODY_STEPS,
    }
def _flatten_to_string(obj: Any, depth: int = 0) -> str:
    """Recursively flatten any JSON-like object into a single string."""
    if depth > 6:
        return ""
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            parts.append(str(k))
            parts.append(_flatten_to_string(v, depth + 1))
        return " ".join(parts)
    if isinstance(obj, list):
        return " ".join(_flatten_to_string(i, depth + 1) for i in obj)
    return str(obj)
def _get_synonyms(incident_type: str) -> List[str]:
    """Return additional keyword synonyms for an incident type."""
    synonyms_map: Dict[str, List[str]] = {
        "ransomware": ["encrypt", "ransom", "locked", "decrypt", "wiper", "crypto"],
        "data_exfiltration": ["exfil", "upload", "transfer", "leak", "dump", "steal", "exfiltrate"],
        "apt_intrusion": ["apt", "nation-state", "targeted", "backdoor", "persistence", "c2", "c&c"],
        "supply_chain_compromise": ["supply chain", "dependency", "package", "solarwinds", "xz", "npm"],
        "credential_compromise": ["credential", "password", "brute force", "spray", "stuffing", "stolen"],
        "lateral_movement": ["lateral", "pivot", "pass-the-hash", "wmi", "psexec", "rdp movement"],
        "priv_escalation": ["privesc", "su_exec", "priv_change", "elevated_session", "priv_grant", "priv_abuse"],
        "malware_detected": ["malware", "trojan", "virus", "worm", "keylogger", "spyware", "rat"],
        "phishing": ["phish", "spear", "bec", "email", "lure", "credential harvest"],
        "unauthorized_access": ["unauthorized", "unauthenticated", "brute", "login failed", "access denied"],
        "policy_violation": ["policy", "dlp", "data loss", "violation", "compliance"],
        "vulnerability_discovered": ["vulnerability", "cve", "exploit", "patch", "zero-day", "rce"],
        "dos_attack": ["dos", "ddos", "flood", "amplification", "bandwidth", "exhaustion"],
        "insider_threat": ["insider", "employee", "contractor", "abuse", "privilege misuse"],
    }
    return synonyms_map.get(incident_type, [])

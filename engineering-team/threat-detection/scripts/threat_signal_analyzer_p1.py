# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_signal_analyzer_base import *  # noqa: F403,E402


MITRE_PATTERN = r'T\d{4}(?:\.\d{3})?'
HUNT_DATA_SOURCES = {
    "initial_access": ["web_proxy_logs", "email_gateway_logs", "firewall_logs", "dns_logs"],
    "execution": ["edr_process_logs", "sysmon_event_1", "windows_event_4688", "auditd"],
    "persistence": ["windows_event_4698", "registry_logs", "cron_logs", "systemd_logs"],
    "privilege_escalation": ["windows_event_4672", "sudo_logs", "auditd", "edr_process_logs"],
    "defense_evasion": ["edr_process_logs", "windows_event_4663", "sysmon_event_11", "antivirus_logs"],
    "credential_access": ["windows_event_4625", "windows_event_4648", "lsass_access_events", "vault_audit_logs"],
    "discovery": ["windows_event_4688", "auditd", "network_flow_logs", "dns_logs"],
    "lateral_movement": ["windows_event_4624", "smb_logs", "winrm_logs", "network_flow_logs"],
    "collection": ["dlp_alerts", "file_access_logs", "clipboard_monitoring", "screen_capture_logs"],
    "command_and_control": ["dns_logs", "proxy_logs", "firewall_logs", "netflow_records"],
    "exfiltration": ["dlp_alerts", "firewall_logs", "proxy_logs", "dns_logs"],
}
IOC_SWEEP_TARGETS = {
    "ip": ["firewall_logs", "netflow_records", "proxy_logs", "threat_intel_platform"],
    "domain": ["dns_logs", "proxy_logs", "email_gateway_logs", "threat_intel_platform"],
    "hash": ["edr_hash_scanning", "antivirus_logs", "file_integrity_monitoring", "threat_intel_platform"],
    "url": ["proxy_logs", "email_gateway_logs", "browser_history_logs"],
    "email": ["email_gateway_logs", "dlp_alerts"],
    "user_agent": ["proxy_logs", "web_application_logs"],
}
IOC_MAX_AGE_DAYS = 30  # IOCs older than this are flagged as stale
HUNT_KEYWORDS = {
    "wmi": {"tactic": "lateral_movement", "mitre": "T1047", "data_source_key": "lateral_movement"},
    "powershell": {"tactic": "execution", "mitre": "T1059.001", "data_source_key": "execution"},
    "lolbin": {"tactic": "defense_evasion", "mitre": "T1218", "data_source_key": "defense_evasion"},
    "lolbas": {"tactic": "defense_evasion", "mitre": "T1218", "data_source_key": "defense_evasion"},
    "pass-the-hash": {"tactic": "lateral_movement", "mitre": "T1550.002", "data_source_key": "lateral_movement"},
    "pth": {"tactic": "lateral_movement", "mitre": "T1550.002", "data_source_key": "lateral_movement"},
    "credential dump": {"tactic": "credential_access", "mitre": "T1003", "data_source_key": "credential_access"},
    "mimikatz": {"tactic": "credential_access", "mitre": "T1003.001", "data_source_key": "credential_access"},
    "lateral": {"tactic": "lateral_movement", "mitre": "T1021", "data_source_key": "lateral_movement"},
    "persistence": {"tactic": "persistence", "mitre": "T1053", "data_source_key": "persistence"},
    "exfil": {"tactic": "exfiltration", "mitre": "T1041", "data_source_key": "exfiltration"},
    "beacon": {"tactic": "command_and_control", "mitre": "T1071", "data_source_key": "command_and_control"},
    "c2": {"tactic": "command_and_control", "mitre": "T1071", "data_source_key": "command_and_control"},
    "ransomware": {"tactic": "impact", "mitre": "T1486", "data_source_key": "execution"},
    "privilege": {"tactic": "privilege_escalation", "mitre": "T1068", "data_source_key": "privilege_escalation"},
    "injection": {"tactic": "defense_evasion", "mitre": "T1055", "data_source_key": "defense_evasion"},
    "apt": {"tactic": "initial_access", "mitre": "T1190", "data_source_key": "initial_access"},
    "supply chain": {"tactic": "initial_access", "mitre": "T1195", "data_source_key": "initial_access"},
    "phishing": {"tactic": "initial_access", "mitre": "T1566", "data_source_key": "initial_access"},
    "scheduled task": {"tactic": "persistence", "mitre": "T1053", "data_source_key": "persistence"},
}
ANOMALY_TIME_HOURS_SUSPICIOUS = list(range(0, 6)) + list(range(22, 24))
def hunt_mode(args):
    """Score and prioritize a threat hunting hypothesis."""
    hypothesis = args.hypothesis or ""
    hypothesis_lower = hypothesis.lower()

    # Extract T-code references via regex
    matched_tcodes = list(set(re.findall(MITRE_PATTERN, hypothesis, re.IGNORECASE)))

    # Keyword matching — multi-word keywords must be checked before single-word
    matched_keywords = []
    seen_keywords = set()
    sorted_keywords = sorted(HUNT_KEYWORDS.keys(), key=lambda k: -len(k))
    for kw in sorted_keywords:
        if kw in hypothesis_lower and kw not in seen_keywords:
            matched_keywords.append(kw)
            seen_keywords.add(kw)

    # Build tactic set from matched keywords and any T-codes that map to known tactics
    tactics = set()
    for kw in matched_keywords:
        tactics.add(HUNT_KEYWORDS[kw]["tactic"])

    # T-codes that happen to be in our keyword map (by mitre field)
    for tcode in matched_tcodes:
        for kw_data in HUNT_KEYWORDS.values():
            if kw_data["mitre"].upper() == tcode.upper():
                tactics.add(kw_data["tactic"])
                break

    # Collect data sources for matched tactics (deduped, ordered)
    data_sources_set = []
    seen_sources = set()
    for tactic in tactics:
        for src in HUNT_DATA_SOURCES.get(tactic, []):
            if src not in seen_sources:
                seen_sources.add(src)
                data_sources_set.append(src)

    # Scoring
    actor_relevance = getattr(args, "actor_relevance", 1)
    control_gap = getattr(args, "control_gap", 1)
    data_availability = getattr(args, "data_availability", 2)

    base_score = len(matched_keywords) * 2 + len(matched_tcodes) * 3
    priority_score = base_score + actor_relevance * 3 + control_gap * 2 + data_availability

    pursue_threshold = 5
    pursue_recommendation = priority_score >= pursue_threshold

    # Data quality check required if no data sources identified or low data_availability
    data_quality_check_required = len(data_sources_set) == 0 or data_availability < 2

    result = {
        "mode": "hunt",
        "hypothesis": hypothesis,
        "matched_keywords": matched_keywords,
        "matched_tcodes": matched_tcodes,
        "tactics": sorted(tactics),
        "data_sources_required": data_sources_set,
        "priority_score": priority_score,
        "pursue_recommendation": pursue_recommendation,
        "data_quality_check_required": data_quality_check_required,
        "score_breakdown": {
            "base_score": base_score,
            "actor_relevance_contribution": actor_relevance * 3,
            "control_gap_contribution": control_gap * 2,
            "data_availability_contribution": data_availability,
            "pursue_threshold": pursue_threshold,
        },
    }
    return result

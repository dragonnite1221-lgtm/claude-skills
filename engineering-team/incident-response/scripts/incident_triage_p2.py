# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402


FALSE_POSITIVE_INDICATORS = [
    {
        "name": "ci_cd_automation",
        "description": "CI/CD pipeline service account activity",
        "patterns": [
            "jenkins", "github-actions", "gitlab-ci", "terraform",
            "ansible", "circleci", "codepipeline",
        ],
    },
    {
        "name": "test_environment",
        "description": "Activity in test/dev/staging environment",
        "patterns": [
            "test", "dev", "staging", "sandbox", "qa", "nonprod", "non-prod",
        ],
    },
    {
        "name": "scheduled_scanner",
        "description": "Known security scanner or automated tool",
        "patterns": [
            "nessus", "qualys", "rapid7", "tenable", "crowdstrike",
            "defender", "sentinel",
        ],
    },
    {
        "name": "scheduled_batch_job",
        "description": "Recurring batch process with expected behavior",
        "patterns": [
            "backup", "sync", "batch", "cron", "scheduled", "nightly", "weekly",
        ],
    },
    {
        "name": "whitelisted_identity",
        "description": "Identity in approved exception list",
        "patterns": [
            "svc-", "sa-", "system@", "automation@", "monitor@", "health-check",
        ],
    },
]
ESCALATION_ROUTING: Dict[str, Dict[str, Any]] = {
    "sev1": {
        "escalate_to": "CISO + CEO + Board Chair (if data at risk)",
        "bridge_call": True,
        "war_room": True,
    },
    "sev2": {
        "escalate_to": "SOC Lead + CISO",
        "bridge_call": True,
        "war_room": False,
    },
    "sev3": {
        "escalate_to": "SOC Lead + Security Manager",
        "bridge_call": False,
        "war_room": False,
    },
    "sev4": {
        "escalate_to": "L3 Analyst queue",
        "bridge_call": False,
        "war_room": False,
    },
}
SEV_ESCALATION_TRIGGERS = [
    {"indicator": "ransomware_note_found", "escalate_to": "sev1"},
    {"indicator": "active_exfiltration_confirmed", "escalate_to": "sev1"},
    {"indicator": "siem_disabled", "escalate_to": "sev1"},
    {"indicator": "domain_controller_access", "escalate_to": "sev1"},
    {"indicator": "second_system_compromised", "escalate_to": "sev1"},
]
def parse_forensic_fields(fact: dict) -> dict:
    """
    Parse and normalise forensic-relevant fields from the raw event.

    Returns a dict with keys: source_ip, destination_ip, user_account,
    hostname, process_name, dwell_hours, iocs, raw_payload.
    """
    raw = fact.get("raw_payload", {}) if isinstance(fact.get("raw_payload"), dict) else {}

    def _pick(*keys: str, default: Any = None) -> Any:
        """Return first non-None value found across fact and raw_payload."""
        for k in keys:
            v = fact.get(k) or raw.get(k)
            if v is not None:
                return v
        return default

    source_ip = _pick("source_ip", "src_ip", "sourceIp", default="unknown")
    destination_ip = _pick("destination_ip", "dst_ip", "dest_ip", "destinationIp", default="unknown")
    user_account = _pick("user", "user_account", "username", "actor", "identity", default="unknown")
    hostname = _pick("hostname", "host", "device", "computer_name", default="unknown")
    process_name = _pick("process", "process_name", "executable", "image", default="unknown")

    # Dwell time: accept hours directly or compute from timestamps
    dwell_hours: float = 0.0
    raw_dwell = _pick("dwell_hours", "dwell_time_hours", "dwell")
    if raw_dwell is not None:
        try:
            dwell_hours = float(raw_dwell)
        except (TypeError, ValueError):
            dwell_hours = 0.0
    else:
        first_seen = _pick("first_seen", "first_observed", "initial_access_time")
        last_seen = _pick("last_seen", "last_observed", "detection_time")
        if first_seen and last_seen:
            try:
                fmt = "%Y-%m-%dT%H:%M:%SZ"
                dt_first = datetime.strptime(str(first_seen), fmt)
                dt_last = datetime.strptime(str(last_seen), fmt)
                dwell_hours = max(0.0, (dt_last - dt_first).total_seconds() / 3600.0)
            except (ValueError, TypeError):
                dwell_hours = 0.0

    iocs: List[str] = []
    raw_iocs = _pick("iocs", "indicators", "indicators_of_compromise")
    if isinstance(raw_iocs, list):
        iocs = [str(i) for i in raw_iocs]
    elif isinstance(raw_iocs, str):
        iocs = [raw_iocs]

    return {
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "user_account": user_account,
        "hostname": hostname,
        "process_name": process_name,
        "dwell_hours": dwell_hours,
        "iocs": iocs,
        "raw_payload": raw,
    }

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from engagement_planner_base import *  # noqa: F403,E402


MITRE_TECHNIQUES = {
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "execution",
               "detection_risk": 0.7, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1059.001": {"name": "PowerShell", "tactic": "execution",
                   "detection_risk": 0.8, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1078": {"name": "Valid Accounts", "tactic": "initial_access",
               "detection_risk": 0.3, "prerequisites": [], "access_level": "external"},
    "T1078.004": {"name": "Valid Accounts: Cloud Accounts", "tactic": "initial_access",
                   "detection_risk": 0.3, "prerequisites": [], "access_level": "external"},
    "T1003": {"name": "OS Credential Dumping", "tactic": "credential_access",
               "detection_risk": 0.9, "prerequisites": ["initial_access", "privilege_escalation"], "access_level": "internal"},
    "T1003.001": {"name": "LSASS Memory", "tactic": "credential_access",
                   "detection_risk": 0.95, "prerequisites": ["initial_access", "privilege_escalation"], "access_level": "credentialed"},
    "T1021": {"name": "Remote Services", "tactic": "lateral_movement",
               "detection_risk": 0.6, "prerequisites": ["initial_access", "credential_access"], "access_level": "internal"},
    "T1021.002": {"name": "SMB/Windows Admin Shares", "tactic": "lateral_movement",
                   "detection_risk": 0.7, "prerequisites": ["initial_access", "credential_access"], "access_level": "internal"},
    "T1055": {"name": "Process Injection", "tactic": "defense_evasion",
               "detection_risk": 0.85, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "initial_access",
               "detection_risk": 0.5, "prerequisites": [], "access_level": "external"},
    "T1566": {"name": "Phishing", "tactic": "initial_access",
               "detection_risk": 0.4, "prerequisites": [], "access_level": "external"},
    "T1566.001": {"name": "Spearphishing Attachment", "tactic": "initial_access",
                   "detection_risk": 0.5, "prerequisites": [], "access_level": "external"},
    "T1098": {"name": "Account Manipulation", "tactic": "persistence",
               "detection_risk": 0.6, "prerequisites": ["initial_access", "privilege_escalation"], "access_level": "credentialed"},
    "T1136": {"name": "Create Account", "tactic": "persistence",
               "detection_risk": 0.7, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "persistence",
               "detection_risk": 0.6, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "impact",
               "detection_risk": 0.99, "prerequisites": ["initial_access", "lateral_movement"], "access_level": "credentialed"},
    "T1530": {"name": "Data from Cloud Storage", "tactic": "collection",
               "detection_risk": 0.4, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "exfiltration",
               "detection_risk": 0.65, "prerequisites": ["initial_access", "collection"], "access_level": "internal"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "exfiltration",
               "detection_risk": 0.5, "prerequisites": ["initial_access", "collection"], "access_level": "internal"},
    "T1083": {"name": "File and Directory Discovery", "tactic": "discovery",
               "detection_risk": 0.3, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1082": {"name": "System Information Discovery", "tactic": "discovery",
               "detection_risk": 0.2, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1057": {"name": "Process Discovery", "tactic": "discovery",
               "detection_risk": 0.25, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1068": {"name": "Exploitation for Privilege Escalation", "tactic": "privilege_escalation",
               "detection_risk": 0.8, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1484": {"name": "Domain Policy Modification", "tactic": "privilege_escalation",
               "detection_risk": 0.85, "prerequisites": ["initial_access", "privilege_escalation"], "access_level": "credentialed"},
    "T1562": {"name": "Impair Defenses", "tactic": "defense_evasion",
               "detection_risk": 0.9, "prerequisites": ["initial_access", "privilege_escalation"], "access_level": "credentialed"},
    "T1070": {"name": "Indicator Removal", "tactic": "defense_evasion",
               "detection_risk": 0.75, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1195": {"name": "Supply Chain Compromise", "tactic": "initial_access",
               "detection_risk": 0.2, "prerequisites": [], "access_level": "external"},
    "T1218": {"name": "System Binary Proxy Execution", "tactic": "defense_evasion",
               "detection_risk": 0.6, "prerequisites": ["initial_access"], "access_level": "internal"},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "command_and_control",
               "detection_risk": 0.55, "prerequisites": ["initial_access"], "access_level": "internal"},
}
ACCESS_LEVEL_HIERARCHY = {"external": 0, "internal": 1, "credentialed": 2}
OPSEC_RISKS = [
    {"risk": "C2 beacon interval too frequent", "severity": "high",
     "mitigation": "Use jitter (25-50%) on beacon intervals; minimum 30s base interval for stealth",
     "relevant_tactics": ["command_and_control"]},
    {"risk": "Infrastructure reuse across engagements", "severity": "critical",
     "mitigation": "Provision fresh C2 infrastructure per engagement; never reuse domains or IPs",
     "relevant_tactics": ["command_and_control", "initial_access"]},
    {"risk": "Scanning during business hours from non-business IP", "severity": "medium",
     "mitigation": "Schedule active scanning to match target business hours and geographic timezone",
     "relevant_tactics": ["discovery"]},
    {"risk": "Known tool signatures in memory or on disk", "severity": "high",
     "mitigation": "Use custom-compiled tools or obfuscated variants; avoid default Cobalt Strike profiles",
     "relevant_tactics": ["execution", "lateral_movement"]},
    {"risk": "Credential dumping without EDR bypass", "severity": "critical",
     "mitigation": "Assess EDR coverage before credential dumping; use protected-mode aware approaches",
     "relevant_tactics": ["credential_access"]},
    {"risk": "Large data transfer without staging", "severity": "high",
     "mitigation": "Stage data locally, compress and encrypt before exfil; avoid single large transfers",
     "relevant_tactics": ["exfiltration", "collection"]},
    {"risk": "Operating outside authorized time window", "severity": "critical",
     "mitigation": "Confirm maintenance and testing windows with client before operational phases",
     "relevant_tactics": []},
    {"risk": "Leaving artifacts in temp directories", "severity": "medium",
     "mitigation": "Clean up all dropped files and created accounts before disengaging",
     "relevant_tactics": ["execution", "persistence"]},
]
KILL_CHAIN_PHASE_ORDER = [
    "initial_access", "execution", "persistence", "privilege_escalation",
    "defense_evasion", "credential_access", "discovery", "lateral_movement",
    "collection", "command_and_control", "exfiltration", "impact"
]
def list_techniques():
    """Print a formatted table of all MITRE techniques and exit."""
    print(f"{'ID':<12} {'Name':<45} {'Tactic':<25} {'Det.Risk':<10} {'Access'}")
    print("-" * 110)
    for tid, data in sorted(MITRE_TECHNIQUES.items()):
        print(
            f"{tid:<12} {data['name']:<45} {data['tactic']:<25} "
            f"{data['detection_risk']:<10.2f} {data['access_level']}"
        )
    sys.exit(0)

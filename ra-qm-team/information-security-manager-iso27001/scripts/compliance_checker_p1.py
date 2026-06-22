# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402


ISO27001_CONTROLS = {
    "organizational": {
        "name": "Organizational Controls",
        "controls": [
            {"id": "A.5.1", "name": "Policies for information security", "priority": "high"},
            {"id": "A.5.2", "name": "Information security roles and responsibilities", "priority": "high"},
            {"id": "A.5.3", "name": "Segregation of duties", "priority": "medium"},
            {"id": "A.5.4", "name": "Management responsibilities", "priority": "high"},
            {"id": "A.5.5", "name": "Contact with authorities", "priority": "medium"},
            {"id": "A.5.6", "name": "Contact with special interest groups", "priority": "low"},
            {"id": "A.5.7", "name": "Threat intelligence", "priority": "medium"},
            {"id": "A.5.8", "name": "Information security in project management", "priority": "medium"},
            {"id": "A.5.9", "name": "Inventory of information and assets", "priority": "high"},
            {"id": "A.5.10", "name": "Acceptable use of information", "priority": "high"},
        ]
    },
    "people": {
        "name": "People Controls",
        "controls": [
            {"id": "A.6.1", "name": "Screening", "priority": "high"},
            {"id": "A.6.2", "name": "Terms and conditions of employment", "priority": "high"},
            {"id": "A.6.3", "name": "Information security awareness and training", "priority": "high"},
            {"id": "A.6.4", "name": "Disciplinary process", "priority": "medium"},
            {"id": "A.6.5", "name": "Responsibilities after termination", "priority": "high"},
            {"id": "A.6.6", "name": "Confidentiality agreements", "priority": "high"},
            {"id": "A.6.7", "name": "Remote working", "priority": "high"},
            {"id": "A.6.8", "name": "Information security event reporting", "priority": "high"},
        ]
    },
    "physical": {
        "name": "Physical Controls",
        "controls": [
            {"id": "A.7.1", "name": "Physical security perimeters", "priority": "high"},
            {"id": "A.7.2", "name": "Physical entry", "priority": "high"},
            {"id": "A.7.3", "name": "Securing offices and facilities", "priority": "medium"},
            {"id": "A.7.4", "name": "Physical security monitoring", "priority": "medium"},
            {"id": "A.7.5", "name": "Protecting against environmental threats", "priority": "medium"},
            {"id": "A.7.6", "name": "Working in secure areas", "priority": "medium"},
            {"id": "A.7.7", "name": "Clear desk and screen", "priority": "medium"},
            {"id": "A.7.8", "name": "Equipment siting and protection", "priority": "medium"},
        ]
    },
    "technological": {
        "name": "Technological Controls",
        "controls": [
            {"id": "A.8.1", "name": "User endpoint devices", "priority": "high"},
            {"id": "A.8.2", "name": "Privileged access rights", "priority": "critical"},
            {"id": "A.8.3", "name": "Information access restriction", "priority": "high"},
            {"id": "A.8.4", "name": "Access to source code", "priority": "high"},
            {"id": "A.8.5", "name": "Secure authentication", "priority": "critical"},
            {"id": "A.8.6", "name": "Capacity management", "priority": "medium"},
            {"id": "A.8.7", "name": "Protection against malware", "priority": "critical"},
            {"id": "A.8.8", "name": "Management of technical vulnerabilities", "priority": "critical"},
            {"id": "A.8.9", "name": "Configuration management", "priority": "high"},
            {"id": "A.8.10", "name": "Information deletion", "priority": "high"},
            {"id": "A.8.11", "name": "Data masking", "priority": "medium"},
            {"id": "A.8.12", "name": "Data leakage prevention", "priority": "high"},
            {"id": "A.8.13", "name": "Information backup", "priority": "critical"},
            {"id": "A.8.14", "name": "Redundancy of information processing", "priority": "high"},
            {"id": "A.8.15", "name": "Logging", "priority": "critical"},
            {"id": "A.8.16", "name": "Monitoring activities", "priority": "high"},
            {"id": "A.8.17", "name": "Clock synchronization", "priority": "medium"},
            {"id": "A.8.18", "name": "Use of privileged utility programs", "priority": "high"},
            {"id": "A.8.19", "name": "Installation of software", "priority": "high"},
            {"id": "A.8.20", "name": "Networks security", "priority": "critical"},
            {"id": "A.8.21", "name": "Security of network services", "priority": "high"},
            {"id": "A.8.22", "name": "Segregation of networks", "priority": "high"},
            {"id": "A.8.23", "name": "Web filtering", "priority": "medium"},
            {"id": "A.8.24", "name": "Use of cryptography", "priority": "critical"},
            {"id": "A.8.25", "name": "Secure development lifecycle", "priority": "high"},
            {"id": "A.8.26", "name": "Application security requirements", "priority": "high"},
            {"id": "A.8.27", "name": "Secure system architecture", "priority": "high"},
            {"id": "A.8.28", "name": "Secure coding", "priority": "high"},
        ]
    },
}
REMEDIATION_GUIDANCE = {
    "A.5.1": "Develop and publish information security policy signed by management",
    "A.5.2": "Define RACI matrix for security roles; appoint Information Security Manager",
    "A.5.9": "Create asset inventory with owners and classification",
    "A.6.3": "Implement annual security awareness training program",
    "A.6.7": "Establish remote working policy with technical controls",
    "A.8.2": "Implement privileged access management (PAM) solution",
    "A.8.5": "Deploy MFA for all user and admin accounts",
    "A.8.7": "Deploy endpoint protection on all devices with central management",
    "A.8.8": "Implement vulnerability scanning with 30-day remediation SLA",
    "A.8.13": "Configure automated backups with encryption and offsite storage",
    "A.8.15": "Deploy SIEM with log retention per compliance requirements",
    "A.8.20": "Implement firewall, IDS/IPS, and network monitoring",
    "A.8.24": "Enforce TLS 1.3 for transit, AES-256 for data at rest",
}
def get_control_status(control_id: str, controls_data: Optional[Dict] = None) -> str:
    """Get implementation status for a control."""
    if controls_data and control_id in controls_data:
        return controls_data[control_id]
    # Default: simulate partial implementation
    import random
    random.seed(hash(control_id))
    statuses = ["implemented", "implemented", "partial", "partial", "not_implemented"]
    return random.choice(statuses)
def load_controls_from_csv(filepath: str) -> Dict[str, str]:
    """Load control status from CSV file."""
    controls = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                control_id = row.get("control_id", row.get("id", ""))
                status = row.get("status", "not_implemented").lower()
                if control_id:
                    controls[control_id] = status
    except FileNotFoundError:
        print(f"Error: Controls file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return controls

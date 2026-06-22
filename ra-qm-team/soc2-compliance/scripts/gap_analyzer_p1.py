# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gap_analyzer_base import *  # noqa: F403,E402


REQUIRED_TSC = {
    "security": {
        "CC1.1": "Integrity and ethical values",
        "CC1.2": "Board oversight",
        "CC1.3": "Organizational structure",
        "CC1.4": "Competence commitment",
        "CC1.5": "Accountability",
        "CC2.1": "Information quality",
        "CC2.2": "Internal communication",
        "CC2.3": "External communication",
        "CC3.1": "Risk objectives",
        "CC3.2": "Risk identification",
        "CC3.3": "Fraud risk consideration",
        "CC3.4": "Change risk assessment",
        "CC4.1": "Monitoring evaluations",
        "CC4.2": "Deficiency communication",
        "CC5.1": "Control activities selection",
        "CC5.2": "Technology controls",
        "CC5.3": "Policy deployment",
        "CC6.1": "Logical access security",
        "CC6.2": "Access provisioning",
        "CC6.3": "Access removal",
        "CC6.4": "Access review",
        "CC6.5": "Physical access",
        "CC6.6": "Encryption",
        "CC6.7": "Data transmission restrictions",
        "CC6.8": "Unauthorized software prevention",
        "CC7.1": "Vulnerability management",
        "CC7.2": "Anomaly monitoring",
        "CC7.3": "Event evaluation",
        "CC7.4": "Incident response",
        "CC7.5": "Incident recovery",
        "CC8.1": "Change management",
        "CC9.1": "Vendor risk management",
        "CC9.2": "Risk mitigation/transfer",
    },
    "availability": {
        "A1.1": "Capacity and performance management",
        "A1.2": "Backup and recovery",
        "A1.3": "Recovery testing",
    },
    "confidentiality": {
        "C1.1": "Confidential data identification",
        "C1.2": "Confidential data protection",
        "C1.3": "Confidential data disposal",
    },
    "processing-integrity": {
        "PI1.1": "Processing accuracy",
        "PI1.2": "Processing completeness",
        "PI1.3": "Processing timeliness",
        "PI1.4": "Processing authorization",
    },
    "privacy": {
        "P1.1": "Privacy notice",
        "P2.1": "Choice and consent",
        "P3.1": "Data collection",
        "P4.1": "Use and retention",
        "P4.2": "Disposal",
        "P5.1": "Access rights",
        "P5.2": "Correction rights",
        "P6.1": "Disclosure controls",
        "P6.2": "Breach notification",
        "P7.1": "Data quality",
        "P8.1": "Privacy monitoring",
    },
}
TYPE2_CHECKS = [
    {
        "check": "evidence_period",
        "description": "Evidence covers the full observation period",
        "severity": "critical",
    },
    {
        "check": "operating_consistency",
        "description": "Control operated consistently throughout the period",
        "severity": "critical",
    },
    {
        "check": "exception_handling",
        "description": "Exceptions are documented and addressed",
        "severity": "high",
    },
    {
        "check": "owner_accountability",
        "description": "Control owners documented and accountable",
        "severity": "medium",
    },
    {
        "check": "evidence_timestamps",
        "description": "Evidence has timestamps within the observation period",
        "severity": "high",
    },
    {
        "check": "frequency_adherence",
        "description": "Control executed at the specified frequency",
        "severity": "critical",
    },
]
def load_controls(filepath: str) -> List[Dict[str, Any]]:
    """Load current controls from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict) and "controls" in data:
        return data["controls"]
    elif isinstance(data, list):
        return data
    else:
        print(
            "Error: Expected JSON with 'controls' array or a plain array.",
            file=sys.stderr,
        )
        sys.exit(1)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from isms_audit_scheduler_base import *  # noqa: F403,E402


CONTROL_DOMAINS = {
    "A.5": {"name": "Organizational Controls", "count": 37},
    "A.6": {"name": "People Controls", "count": 8},
    "A.7": {"name": "Physical Controls", "count": 14},
    "A.8": {"name": "Technological Controls", "count": 34},
}
DEFAULT_RISK_RATINGS = {
    "A.5.1": {"name": "Policies for information security", "risk": "medium"},
    "A.5.2": {"name": "Information security roles", "risk": "medium"},
    "A.5.15": {"name": "Access control", "risk": "high"},
    "A.5.24": {"name": "Incident management planning", "risk": "high"},
    "A.5.25": {"name": "Assessment of security events", "risk": "high"},
    "A.6.1": {"name": "Screening", "risk": "medium"},
    "A.6.3": {"name": "Information security awareness", "risk": "medium"},
    "A.6.7": {"name": "Remote working", "risk": "high"},
    "A.7.1": {"name": "Physical security perimeters", "risk": "medium"},
    "A.7.4": {"name": "Physical security monitoring", "risk": "medium"},
    "A.8.2": {"name": "Privileged access rights", "risk": "critical"},
    "A.8.5": {"name": "Secure authentication", "risk": "critical"},
    "A.8.7": {"name": "Protection against malware", "risk": "high"},
    "A.8.8": {"name": "Management of vulnerabilities", "risk": "critical"},
    "A.8.13": {"name": "Information backup", "risk": "high"},
    "A.8.15": {"name": "Logging", "risk": "critical"},
    "A.8.20": {"name": "Networks security", "risk": "high"},
    "A.8.24": {"name": "Use of cryptography", "risk": "high"},
}
AUDIT_FREQUENCY = {
    "critical": 4,  # Quarterly
    "high": 2,      # Semi-annual
    "medium": 1,    # Annual
    "low": 1,       # Annual
}
def load_controls_from_csv(filepath: str) -> Dict[str, Dict]:
    """Load control risk ratings from CSV file."""
    controls = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                control_id = row.get("control_id", row.get("id", ""))
                if control_id:
                    controls[control_id] = {
                        "name": row.get("name", "Unknown"),
                        "risk": row.get("risk", "medium").lower(),
                    }
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return controls
def calculate_audit_dates(
    year: int,
    frequency: int
) -> List[str]:
    """Calculate audit dates based on frequency."""
    dates = []
    interval = 12 // frequency
    for i in range(frequency):
        month = (i * interval) + 2  # Start in February
        if month > 12:
            month = month - 12
        date = datetime(year, month, 15)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

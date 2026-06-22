# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_assessment_base import *  # noqa: F403,E402


THREAT_CATALOGS = {
    "general": [
        {"id": "T01", "name": "Unauthorized access", "category": "Access", "likelihood": 4},
        {"id": "T02", "name": "Data breach", "category": "Confidentiality", "likelihood": 3},
        {"id": "T03", "name": "Malware infection", "category": "Integrity", "likelihood": 4},
        {"id": "T04", "name": "Phishing attack", "category": "Social Engineering", "likelihood": 5},
        {"id": "T05", "name": "Denial of service", "category": "Availability", "likelihood": 3},
        {"id": "T06", "name": "Insider threat", "category": "Personnel", "likelihood": 2},
        {"id": "T07", "name": "Physical theft", "category": "Physical", "likelihood": 2},
        {"id": "T08", "name": "System misconfiguration", "category": "Technical", "likelihood": 4},
        {"id": "T09", "name": "Third-party compromise", "category": "Supply Chain", "likelihood": 3},
        {"id": "T10", "name": "Natural disaster", "category": "Environmental", "likelihood": 1},
    ],
    "healthcare": [
        {"id": "T01", "name": "Patient data breach", "category": "Confidentiality", "likelihood": 4},
        {"id": "T02", "name": "Ransomware attack", "category": "Availability", "likelihood": 4},
        {"id": "T03", "name": "Medical device tampering", "category": "Integrity", "likelihood": 3},
        {"id": "T04", "name": "EHR unauthorized access", "category": "Access", "likelihood": 4},
        {"id": "T05", "name": "HIPAA violation", "category": "Compliance", "likelihood": 3},
        {"id": "T06", "name": "Clinical data corruption", "category": "Integrity", "likelihood": 2},
        {"id": "T07", "name": "Telemedicine interception", "category": "Confidentiality", "likelihood": 3},
        {"id": "T08", "name": "Credential theft", "category": "Access", "likelihood": 5},
        {"id": "T09", "name": "Third-party vendor breach", "category": "Supply Chain", "likelihood": 3},
        {"id": "T10", "name": "Insider data theft", "category": "Personnel", "likelihood": 2},
    ],
    "cloud": [
        {"id": "T01", "name": "Cloud misconfiguration", "category": "Technical", "likelihood": 5},
        {"id": "T02", "name": "API vulnerability exploit", "category": "Application", "likelihood": 4},
        {"id": "T03", "name": "Account hijacking", "category": "Access", "likelihood": 4},
        {"id": "T04", "name": "Data exfiltration", "category": "Confidentiality", "likelihood": 3},
        {"id": "T05", "name": "Shared tenancy attack", "category": "Infrastructure", "likelihood": 2},
        {"id": "T06", "name": "Service outage", "category": "Availability", "likelihood": 3},
        {"id": "T07", "name": "Compliance violation", "category": "Compliance", "likelihood": 3},
        {"id": "T08", "name": "Shadow IT exposure", "category": "Governance", "likelihood": 4},
        {"id": "T09", "name": "Encryption key exposure", "category": "Cryptography", "likelihood": 2},
        {"id": "T10", "name": "CSP vendor lock-in", "category": "Strategic", "likelihood": 3},
    ],
}
VULNERABILITY_PATTERNS = {
    "access": ["No MFA", "Weak passwords", "Excessive privileges", "Shared accounts"],
    "technical": ["Unpatched systems", "Weak encryption", "Missing logging", "Open ports"],
    "process": ["No incident response", "Missing backups", "No change control", "Lack of monitoring"],
    "people": ["Untrained staff", "No security awareness", "Social engineering susceptibility"],
}
CLASSIFICATION_CRITERIA = {
    "critical": {"description": "Business-critical, severe impact if compromised", "impact": 5},
    "high": {"description": "Important assets, significant impact", "impact": 4},
    "medium": {"description": "Standard business assets, moderate impact", "impact": 3},
    "low": {"description": "Limited business value, minor impact", "impact": 2},
    "minimal": {"description": "Public or non-sensitive, negligible impact", "impact": 1},
}
TREATMENT_OPTIONS = {
    "critical": "Immediate mitigation required - implement controls within 7 days",
    "high": "Priority mitigation - implement controls within 30 days",
    "medium": "Planned mitigation - implement controls within 90 days",
    "low": "Accept risk with monitoring or implement low-cost controls",
    "minimal": "Accept risk - document acceptance decision",
}
def calculate_risk_score(likelihood: int, impact: int) -> int:
    """Calculate risk score as likelihood × impact."""
    return likelihood * impact
def get_risk_level(score: int) -> str:
    """Determine risk level from score."""
    if score >= 20:
        return "critical"
    elif score >= 15:
        return "high"
    elif score >= 10:
        return "medium"
    elif score >= 5:
        return "low"
    return "minimal"
def load_assets_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """Load asset inventory from CSV file."""
    assets = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                asset = {
                    "id": row.get("id", f"A{len(assets)+1:03d}"),
                    "name": row.get("name", "Unknown"),
                    "type": row.get("type", "Information"),
                    "owner": row.get("owner", "Unassigned"),
                    "classification": row.get("classification", "medium").lower(),
                }
                assets.append(asset)
    except FileNotFoundError:
        print(f"Error: Asset file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading asset file: {e}", file=sys.stderr)
        sys.exit(1)
    return assets

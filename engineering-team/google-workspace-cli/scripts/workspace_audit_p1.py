# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from workspace_audit_base import *  # noqa: F403,E402


@dataclass
class AuditFinding:
    area: str
    check: str
    status: str  # PASS, WARN, FAIL
    message: str
    risk: str = ""
    remediation: str = ""
@dataclass
class AuditReport:
    findings: List[dict] = field(default_factory=list)
    score: int = 0
    max_score: int = 100
    grade: str = ""
    summary: str = ""
    demo_mode: bool = False
DEMO_FINDINGS = [
    AuditFinding("drive", "External sharing", "WARN",
                 "External sharing is enabled for the domain",
                 "Data exfiltration via shared links",
                 "Review sharing settings in Admin Console > Apps > Google Workspace > Drive"),
    AuditFinding("drive", "Link sharing defaults", "FAIL",
                 "Default link sharing is set to 'Anyone with the link'",
                 "Sensitive files accessible without authentication",
                 "gws admin settings update drive --defaultLinkSharing restricted"),
    AuditFinding("gmail", "Auto-forwarding", "PASS",
                 "No auto-forwarding rules detected for admin accounts"),
    AuditFinding("gmail", "SPF record", "PASS",
                 "SPF record configured correctly"),
    AuditFinding("gmail", "DMARC record", "WARN",
                 "DMARC policy is set to 'none' (monitoring only)",
                 "Email spoofing not actively blocked",
                 "Update DMARC DNS record: v=DMARC1; p=quarantine; rua=mailto:dmarc@company.com"),
    AuditFinding("gmail", "DKIM signing", "PASS",
                 "DKIM signing is enabled"),
    AuditFinding("calendar", "Default visibility", "WARN",
                 "Calendar default visibility is 'See all event details'",
                 "Meeting details visible to all domain users",
                 "Admin Console > Apps > Calendar > Sharing settings > Set to 'Free/Busy'"),
    AuditFinding("calendar", "External sharing", "PASS",
                 "External calendar sharing is restricted"),
    AuditFinding("oauth", "Third-party apps", "FAIL",
                 "12 third-party OAuth apps with broad access detected",
                 "Unauthorized data access via OAuth grants",
                 "Review: Admin Console > Security > API controls > App access control"),
    AuditFinding("oauth", "High-risk apps", "WARN",
                 "3 apps have Drive full access scope",
                 "Apps can read/modify all Drive files",
                 "Audit each app: gws admin tokens list --json | filter by scope"),
    AuditFinding("admin", "Super admin count", "WARN",
                 "4 super admin accounts detected (recommended: 2-3)",
                 "Increased attack surface for privilege escalation",
                 "Reduce super admins: gws admin users list --query 'isAdmin=true' --json"),
    AuditFinding("admin", "2-Step verification", "PASS",
                 "2-Step verification enforced for all users"),
    AuditFinding("admin", "Password policy", "PASS",
                 "Minimum password length: 12 characters"),
    AuditFinding("admin", "Login challenges", "PASS",
                 "Suspicious login challenges enabled"),
]
def run_gws_command(cmd: List[str]) -> Optional[str]:
    """Run a gws command and return stdout, or None on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            return result.stdout
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
def audit_drive() -> List[AuditFinding]:
    """Audit Drive sharing and security settings."""
    findings = []

    # Check sharing settings
    output = run_gws_command(["gws", "drive", "about", "get", "--json"])
    if output:
        try:
            data = json.loads(output)
            # Check if external sharing is enabled
            if data.get("canShareOutsideDomain", True):
                findings.append(AuditFinding(
                    "drive", "External sharing", "WARN",
                    "External sharing is enabled",
                    "Data exfiltration via shared links",
                    "Review Admin Console > Apps > Drive > Sharing settings"
                ))
            else:
                findings.append(AuditFinding(
                    "drive", "External sharing", "PASS",
                    "External sharing is restricted"
                ))
        except json.JSONDecodeError:
            findings.append(AuditFinding(
                "drive", "External sharing", "WARN",
                "Could not parse Drive settings"
            ))
    else:
        findings.append(AuditFinding(
            "drive", "External sharing", "WARN",
            "Could not retrieve Drive settings"
        ))

    return findings

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from auth_setup_guide_base import *  # noqa: F403,E402


ENV_TEMPLATE = """# Google Workspace CLI Configuration
# Copy to .env and fill in values

# OAuth Credentials (for interactive auth)
GWS_CLIENT_ID=
GWS_CLIENT_SECRET=
GWS_TOKEN_PATH=~/.config/gws/token.json

# Service Account (for headless/CI auth)
# GWS_SERVICE_ACCOUNT_KEY=/path/to/key.json
# GWS_DELEGATED_USER=admin@yourdomain.com

# Defaults
GWS_DEFAULT_FORMAT=json
GWS_PAGINATION_LIMIT=100
"""
@dataclass
class ValidationResult:
    service: str
    status: str  # PASS, FAIL
    message: str
@dataclass
class ValidationReport:
    auth_method: str = ""
    user: str = ""
    results: List[dict] = field(default_factory=list)
    summary: str = ""
    demo_mode: bool = False
DEMO_VALIDATION = ValidationReport(
    auth_method="oauth",
    user="admin@company.com",
    results=[
        {"service": "gmail", "status": "PASS", "message": "Gmail API accessible"},
        {"service": "drive", "status": "PASS", "message": "Drive API accessible"},
        {"service": "calendar", "status": "PASS", "message": "Calendar API accessible"},
        {"service": "sheets", "status": "PASS", "message": "Sheets API accessible"},
        {"service": "tasks", "status": "FAIL", "message": "Scope not authorized"},
    ],
    summary="4/5 services validated (demo mode)",
    demo_mode=True,
)
def check_auth_status() -> dict:
    """Check current gws auth status."""
    try:
        result = subprocess.run(
            ["gws", "auth", "status", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"status": "authenticated", "raw": result.stdout.strip()}
        return {"status": "not_authenticated", "error": result.stderr.strip()[:200]}
    except (FileNotFoundError, OSError):
        return {"status": "gws_not_found"}
def validate_services(services: List[str]) -> ValidationReport:
    """Validate auth by testing each service."""
    report = ValidationReport()

    auth = check_auth_status()
    if auth.get("status") == "gws_not_found":
        report.summary = "gws CLI not installed"
        return report
    if auth.get("status") == "not_authenticated":
        report.auth_method = "none"
        report.summary = "Not authenticated"
        return report

    report.auth_method = auth.get("method", "oauth")
    report.user = auth.get("user", auth.get("email", "unknown"))

    service_cmds = {
        "gmail": ["gws", "gmail", "users", "getProfile", "me", "--json"],
        "drive": ["gws", "drive", "files", "list", "--limit", "1", "--json"],
        "calendar": ["gws", "calendar", "calendarList", "list", "--limit", "1", "--json"],
        "sheets": ["gws", "sheets", "spreadsheets", "get", "test", "--json"],
        "tasks": ["gws", "tasks", "tasklists", "list", "--limit", "1", "--json"],
    }

    for svc in services:
        cmd = service_cmds.get(svc)
        if not cmd:
            report.results.append(asdict(
                ValidationResult(svc, "WARN", f"No test available for {svc}")
            ))
            continue
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                report.results.append(asdict(
                    ValidationResult(svc, "PASS", f"{svc.title()} API accessible")
                ))
            else:
                report.results.append(asdict(
                    ValidationResult(svc, "FAIL", result.stderr.strip()[:100])
                ))
        except (subprocess.TimeoutExpired, OSError) as e:
            report.results.append(asdict(
                ValidationResult(svc, "FAIL", str(e)[:100])
            ))

    passed = sum(1 for r in report.results if r["status"] == "PASS")
    total = len(report.results)
    report.summary = f"{passed}/{total} services validated"
    return report

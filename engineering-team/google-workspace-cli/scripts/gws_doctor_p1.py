# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_doctor_base import *  # noqa: F403,E402


@dataclass
class Check:
    name: str
    status: str  # PASS, WARN, FAIL
    message: str
    fix: str = ""
@dataclass
class DiagnosticReport:
    gws_installed: bool = False
    gws_version: str = ""
    auth_status: str = ""
    checks: List[dict] = field(default_factory=list)
    summary: str = ""
    demo_mode: bool = False
DEMO_CHECKS = [
    Check("gws-installed", "PASS", "gws v0.9.2 found at /usr/local/bin/gws"),
    Check("gws-version", "PASS", "Version 0.9.2 (latest)"),
    Check("auth-status", "PASS", "Authenticated as admin@company.com"),
    Check("token-expiry", "WARN", "Token expires in 23 minutes",
          "Run 'gws auth refresh' to extend token lifetime"),
    Check("gmail-access", "PASS", "Gmail API accessible — user profile retrieved"),
    Check("drive-access", "PASS", "Drive API accessible — root folder listed"),
    Check("calendar-access", "PASS", "Calendar API accessible — primary calendar found"),
    Check("sheets-access", "PASS", "Sheets API accessible"),
    Check("tasks-access", "FAIL", "Tasks API not authorized",
          "Run 'gws auth setup' and add 'tasks' scope"),
]
SERVICE_TEST_COMMANDS = {
    "gmail": ["gws", "gmail", "users", "getProfile", "me", "--json"],
    "drive": ["gws", "drive", "files", "list", "--limit", "1", "--json"],
    "calendar": ["gws", "calendar", "calendarList", "list", "--limit", "1", "--json"],
    "sheets": ["gws", "sheets", "spreadsheets", "get", "test", "--json"],
    "tasks": ["gws", "tasks", "tasklists", "list", "--limit", "1", "--json"],
    "chat": ["gws", "chat", "spaces", "list", "--limit", "1", "--json"],
    "docs": ["gws", "docs", "documents", "get", "test", "--json"],
}
def check_installation() -> Check:
    """Check if gws is installed and on PATH."""
    path = shutil.which("gws")
    if path:
        return Check("gws-installed", "PASS", f"gws found at {path}")
    return Check("gws-installed", "FAIL", "gws not found on PATH",
                 "Install via: cargo install gws-cli  OR  download from https://github.com/googleworkspace/cli/releases")
def check_version() -> Check:
    """Get gws version."""
    try:
        result = subprocess.run(
            ["gws", "--version"], capture_output=True, text=True, timeout=10
        )
        version = result.stdout.strip()
        if version:
            return Check("gws-version", "PASS", f"Version: {version}")
        return Check("gws-version", "WARN", "Could not parse version output")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return Check("gws-version", "FAIL", f"Version check failed: {e}")
def check_auth() -> Check:
    """Check authentication status."""
    try:
        result = subprocess.run(
            ["gws", "auth", "status", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                user = data.get("user", data.get("email", "unknown"))
                return Check("auth-status", "PASS", f"Authenticated as {user}")
            except json.JSONDecodeError:
                return Check("auth-status", "PASS", "Authenticated (could not parse details)")
        return Check("auth-status", "FAIL", "Not authenticated",
                     "Run 'gws auth setup' to configure authentication")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return Check("auth-status", "FAIL", f"Auth check failed: {e}",
                     "Run 'gws auth setup' to configure authentication")
def check_service(service: str) -> Check:
    """Test connectivity to a specific service."""
    cmd = SERVICE_TEST_COMMANDS.get(service)
    if not cmd:
        return Check(f"{service}-access", "WARN", f"No test command for {service}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return Check(f"{service}-access", "PASS", f"{service.title()} API accessible")
        stderr = result.stderr.strip()[:100]
        if "403" in stderr or "permission" in stderr.lower():
            return Check(f"{service}-access", "FAIL",
                         f"{service.title()} API permission denied",
                         f"Add '{service}' scope: gws auth setup --scopes {service}")
        return Check(f"{service}-access", "FAIL",
                     f"{service.title()} API error: {stderr}",
                     f"Check scope and permissions for {service}")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return Check(f"{service}-access", "FAIL", f"{service.title()} test failed: {e}")

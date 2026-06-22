# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pr_analyzer_base import *  # noqa: F403,E402


FILE_CATEGORIES = {
    "critical": {
        "patterns": [
            r"auth", r"security", r"password", r"token", r"secret",
            r"payment", r"billing", r"crypto", r"encrypt"
        ],
        "weight": 5,
        "description": "Security-sensitive files requiring careful review"
    },
    "high": {
        "patterns": [
            r"api", r"database", r"migration", r"schema", r"model",
            r"config", r"env", r"middleware"
        ],
        "weight": 4,
        "description": "Core infrastructure files"
    },
    "medium": {
        "patterns": [
            r"service", r"controller", r"handler", r"util", r"helper"
        ],
        "weight": 3,
        "description": "Business logic files"
    },
    "low": {
        "patterns": [
            r"test", r"spec", r"mock", r"fixture", r"story",
            r"readme", r"docs", r"\.md$"
        ],
        "weight": 1,
        "description": "Tests and documentation"
    }
}
RISK_PATTERNS = [
    {
        "name": "hardcoded_secrets",
        "pattern": r"(password|secret|api_key|token)\s*[=:]\s*['\"][^'\"]+['\"]",
        "severity": "critical",
        "message": "Potential hardcoded secret detected"
    },
    {
        "name": "todo_fixme",
        "pattern": r"(TODO|FIXME|HACK|XXX):",
        "severity": "low",
        "message": "TODO/FIXME comment found"
    },
    {
        "name": "console_log",
        "pattern": r"console\.(log|debug|info|warn|error)\(",
        "severity": "medium",
        "message": "Console statement found (remove for production)"
    },
    {
        "name": "debugger",
        "pattern": r"\bdebugger\b",
        "severity": "high",
        "message": "Debugger statement found"
    },
    {
        "name": "disable_eslint",
        "pattern": r"eslint-disable",
        "severity": "medium",
        "message": "ESLint rule disabled"
    },
    {
        "name": "any_type",
        "pattern": r":\s*any\b",
        "severity": "medium",
        "message": "TypeScript 'any' type used"
    },
    {
        "name": "sql_concatenation",
        "pattern": r"(SELECT|INSERT|UPDATE|DELETE).*\+.*['\"]",
        "severity": "critical",
        "message": "Potential SQL injection (string concatenation in query)"
    }
]
def run_git_command(cmd: List[str], cwd: Path) -> Tuple[bool, str]:
    """Run a git command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

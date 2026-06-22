# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import Severity  # noqa: E402,E501
# fmt: on


def _mod_cg0_1():
    return [
        {
        "regex": r"\bsocket\.(?:connect|create_connection)\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Raw socket connection — potential C2 or exfiltration channel",
        "fix": "Remove raw socket usage unless absolutely required and justified",
    },
        {
        "regex": r"\bhttpx\.(?:post|put|patch|AsyncClient)\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Outbound HTTP request via httpx",
        "fix": "Remove or verify destination is trusted",
    },
        {
        "regex": r"\baiohttp\.ClientSession\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Async HTTP client — potential exfiltration",
        "fix": "Remove or verify all request destinations are trusted",
    },
        {
        "regex": r"\brequests\.get\s*\(",
        "category": "NET-READ",
        "severity": Severity.HIGH,
        "risk": "Outbound HTTP GET request — may download malicious payloads",
        "fix": "Verify the URL is trusted and necessary for skill functionality",
    },
        {
        "regex": r"(?:open|read|Path)\s*\([^)]*(?:\.ssh|\.aws|\.config/secrets|\.gnupg|\.npmrc|\.pypirc)",
        "category": "CRED-HARVEST",
        "severity": Severity.CRITICAL,
        "risk": "Reads credential files (SSH keys, AWS creds, secrets)",
        "fix": "Remove all access to credential directories",
    },
        {
        "regex": r"\bos\.environ\s*\[\s*['\"](?:AWS_|GITHUB_TOKEN|API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE)",
        "category": "CRED-HARVEST",
        "severity": Severity.CRITICAL,
        "risk": "Extracts sensitive environment variables",
        "fix": "Remove credential access unless skill explicitly requires it and user is warned",
    },
        {
        "regex": r"\bos\.environ\.get\s*\([^)]*(?:AWS_|GITHUB_TOKEN|API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE)",
        "category": "CRED-HARVEST",
        "severity": Severity.CRITICAL,
        "risk": "Reads sensitive environment variables",
        "fix": "Remove credential access. Skills should not need external credentials",
    },
        {
        "regex": r"(?:keyring|keychain)\.\w+\s*\(",
        "category": "CRED-HARVEST",
        "severity": Severity.CRITICAL,
        "risk": "Accesses system keyring/keychain",
        "fix": "Remove keyring access — skills should not access system credential stores",
    },
        {
        "regex": r"(?:open|write|Path)\s*\([^)]*(?:/etc/|/usr/|/var/|/tmp/\.\w)",
        "category": "FS-ABUSE",
        "severity": Severity.HIGH,
        "risk": "Writes to system directories outside skill scope",
        "fix": "Restrict file operations to the skill directory or user-specified output paths",
    },
        {
        "regex": r"(?:open|write|Path)\s*\([^)]*(?:\.bashrc|\.bash_profile|\.profile|\.zshrc|\.zprofile)",
        "category": "FS-ABUSE",
        "severity": Severity.CRITICAL,
        "risk": "Modifies shell configuration — potential persistence mechanism",
        "fix": "Remove all writes to shell config files",
    },
        {
        "regex": r"\bos\.symlink\s*\(",
        "category": "FS-ABUSE",
        "severity": Severity.HIGH,
        "risk": "Creates symbolic links — potential directory traversal attack",
        "fix": "Remove symlink creation unless explicitly required and bounded",
    },
        {
        "regex": r"\bshutil\.rmtree\s*\(",
        "category": "FS-ABUSE",
        "severity": Severity.HIGH,
        "risk": "Recursive directory deletion — destructive operation",
        "fix": "Remove or restrict to specific, validated paths within skill scope",
    },
        {
        "regex": r"\bos\.remove\s*\(|os\.unlink\s*\(",
        "category": "FS-ABUSE",
        "severity": Severity.HIGH,
        "risk": "File deletion — verify target is within skill scope",
        "fix": "Ensure deletion targets are validated and within expected paths",
    },
        {
        "regex": r"\bsudo\b",
        "category": "PRIV-ESC",
        "severity": Severity.CRITICAL,
        "risk": "Sudo invocation — privilege escalation attempt",
        "fix": "Remove sudo usage. Skills should never require elevated privileges",
    },
        {
        "regex": r"\bchmod\b.*\b[0-7]*7[0-7]{2}\b",
        "category": "PRIV-ESC",
        "severity": Severity.HIGH,
        "risk": "Setting world-executable permissions",
        "fix": "Use restrictive permissions (e.g., 0o644 for files, 0o755 for dirs)",
    },
        {
        "regex": r"\bos\.set(?:e)?uid\s*\(",
        "category": "PRIV-ESC",
        "severity": Severity.CRITICAL,
        "risk": "UID manipulation — privilege escalation",
        "fix": "Remove UID manipulation. Skills must run as the invoking user",
    },
        {
        "regex": r"\bcrontab\b|\bcron\b.*\bwrite\b",
        "category": "PRIV-ESC",
        "severity": Severity.CRITICAL,
        "risk": "Cron job manipulation — persistence mechanism",
        "fix": "Remove cron manipulation. Skills should not modify scheduled tasks",
    },
    ]

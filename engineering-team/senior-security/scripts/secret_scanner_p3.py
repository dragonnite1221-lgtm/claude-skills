# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from secret_scanner_base import *  # noqa: F403,E402
# fmt: off
from secret_scanner_p1 import SecretFinding, SecretPattern, Severity  # noqa: E402,E501
from secret_scanner_p2 import _mod_cg0_0  # noqa: E402,E501
# fmt: on


def _mod_cg0_1():
    return [
        SecretPattern(
        pattern_id="CRYPTO003",
        name="OpenSSH Private Key",
        description="OpenSSH private key",
        regex=r'-----BEGIN OPENSSH PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".pem", ".key", ".txt"],
        recommendation="Never commit SSH keys to repositories"
    ),
        SecretPattern(
        pattern_id="CRYPTO004",
        name="PGP Private Key",
        description="PGP/GPG private key block",
        regex=r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".asc", ".gpg", ".txt"],
        recommendation="Store PGP keys in secure key rings, not source code"
    ),
        SecretPattern(
        pattern_id="GEN001",
        name="Generic API Key",
        description="Generic API key or secret pattern",
        regex=r'(?:api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json", ".xml"],
        recommendation="Use environment variables or secrets manager"
    ),
        SecretPattern(
        pattern_id="GEN002",
        name="Generic Secret",
        description="Generic secret or token pattern",
        regex=r'(?:secret|token|auth[_-]?token)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Store secrets in environment variables or secret managers"
    ),
        SecretPattern(
        pattern_id="GEN003",
        name="Password in Config",
        description="Password in configuration file",
        regex=r'(?:password|passwd|pwd)\s*[:=]\s*["\'][^"\']{8,}["\']',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json", ".xml", ".conf", ".ini"],
        recommendation="Never hardcode passwords. Use secret managers"
    ),
        SecretPattern(
        pattern_id="GEN004",
        name="Database Connection String",
        description="Database connection string with credentials",
        regex=r'(?:mongodb|postgres|mysql|redis|amqp)://[^:]+:[^@]+@[^/]+',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use environment variables for database credentials"
    ),
        SecretPattern(
        pattern_id="LOW001",
        name="TODO with Secret",
        description="TODO comment mentioning secrets or credentials",
        regex=r'(?:#|//|/\*)\s*(?:TODO|FIXME|XXX).*(?:secret|password|credential|key)',
        severity=Severity.LOW,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php"],
        recommendation="Address security TODOs before deployment"
    ),
    ]
SECRET_PATTERNS = (_mod_cg0_0() + _mod_cg0_1())
def scan_file(file_path: Path, patterns: List[SecretPattern]) -> List[SecretFinding]:
    """Scan a single file for secrets."""
    findings = []
    extension = file_path.suffix.lower()

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception:
        return findings

    for pattern in patterns:
        if extension not in pattern.file_extensions:
            continue

        try:
            regex = re.compile(pattern.regex, re.IGNORECASE)

            for i, line in enumerate(lines, 1):
                # Skip comments that explain patterns (like in this file)
                if 'regex' in line.lower() or 'pattern' in line.lower():
                    continue

                match = regex.search(line)
                if match:
                    # Mask the actual secret for safety
                    matched = match.group(0)
                    if len(matched) > 20:
                        masked = matched[:10] + "..." + matched[-5:]
                    else:
                        masked = matched[:5] + "..."

                    findings.append(SecretFinding(
                        pattern_id=pattern.pattern_id,
                        name=pattern.name,
                        severity=pattern.severity,
                        file_path=str(file_path),
                        line_number=i,
                        matched_text=masked,
                        recommendation=pattern.recommendation
                    ))
        except re.error:
            continue

    return findings

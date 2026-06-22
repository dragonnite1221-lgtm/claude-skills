# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from secret_scanner_base import *  # noqa: F403,E402
# fmt: off
from secret_scanner_p1 import SecretPattern, Severity  # noqa: E402,E501
# fmt: on


def _mod_cg0_0():
    return [
        SecretPattern(
        pattern_id="AWS001",
        name="AWS Access Key ID",
        description="AWS access key identifier",
        regex=r'AKIA[0-9A-Z]{16}',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json", ".xml", ".conf"],
        recommendation="Use IAM roles or AWS Secrets Manager instead of hardcoded keys"
    ),
        SecretPattern(
        pattern_id="AWS002",
        name="AWS Secret Access Key",
        description="AWS secret access key",
        regex=r'(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*["\']?[A-Za-z0-9/+=]{40}["\']?',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json", ".conf"],
        recommendation="Use IAM roles or AWS Secrets Manager instead of hardcoded secrets"
    ),
        SecretPattern(
        pattern_id="GCP001",
        name="Google Cloud API Key",
        description="Google Cloud Platform API key",
        regex=r'AIza[0-9A-Za-z\-_]{35}',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use service accounts or Google Secret Manager"
    ),
        SecretPattern(
        pattern_id="AZURE001",
        name="Azure Storage Key",
        description="Azure storage account key",
        regex=r'(?:AccountKey|account_key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{88}["\']?',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".cs", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use Azure Key Vault or managed identities"
    ),
        SecretPattern(
        pattern_id="JWT001",
        name="JSON Web Token",
        description="Hardcoded JWT token",
        regex=r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".json"],
        recommendation="Generate tokens dynamically, never hardcode"
    ),
        SecretPattern(
        pattern_id="GITHUB001",
        name="GitHub Token",
        description="GitHub personal access token or OAuth token",
        regex=r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use GitHub App authentication or environment variables"
    ),
        SecretPattern(
        pattern_id="GITLAB001",
        name="GitLab Token",
        description="GitLab personal access or pipeline token",
        regex=r'glpat-[A-Za-z0-9\-_]{20,}',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml"],
        recommendation="Use CI/CD variables or environment variables"
    ),
        SecretPattern(
        pattern_id="SLACK001",
        name="Slack Token",
        description="Slack API token",
        regex=r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use environment variables or secrets manager"
    ),
        SecretPattern(
        pattern_id="STRIPE001",
        name="Stripe API Key",
        description="Stripe secret or publishable key",
        regex=r'(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24,}',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use environment variables, never commit API keys"
    ),
        SecretPattern(
        pattern_id="TWILIO001",
        name="Twilio API Key",
        description="Twilio account SID or auth token",
        regex=r'(?:AC[a-z0-9]{32}|SK[a-z0-9]{32})',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use environment variables for Twilio credentials"
    ),
        SecretPattern(
        pattern_id="SENDGRID001",
        name="SendGrid API Key",
        description="SendGrid API key",
        regex=r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
        severity=Severity.HIGH,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json"],
        recommendation="Use environment variables for email service credentials"
    ),
        SecretPattern(
        pattern_id="CRYPTO001",
        name="RSA Private Key",
        description="RSA private key in PEM format",
        regex=r'-----BEGIN RSA PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".pem", ".key", ".txt"],
        recommendation="Store private keys in secure key management systems"
    ),
        SecretPattern(
        pattern_id="CRYPTO002",
        name="EC Private Key",
        description="Elliptic curve private key",
        regex=r'-----BEGIN EC PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        file_extensions=[".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".pem", ".key"],
        recommendation="Use hardware security modules or key management services"
    ),
    ]

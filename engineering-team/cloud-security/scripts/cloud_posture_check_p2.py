# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402


DATA_EXFILTRATION_ACTIONS: List[str] = [
    "s3:GetObject",
    "s3:ListBucket",
    "s3:GetBucketAcl",
    "s3:GetObjectAcl",
    "s3:GetBucketPolicy",
    "s3:PutBucketPolicy",
    "s3:PutBucketAcl",
    "s3:PutObjectAcl",
    "s3:CopyObject",
    "s3:HeadObject",
    "rds:DescribeDBInstances",
    "rds:DownloadDBLogFilePortion",
    "rds:DescribeDBSnapshots",
    "rds:RestoreDBInstanceFromDBSnapshot",
    "dynamodb:Scan",
    "dynamodb:Query",
    "dynamodb:GetItem",
    "dynamodb:BatchGetItem",
    "ec2:DescribeInstances",
    "ec2:DescribeSnapshots",
    "ec2:CreateSnapshot",
    "ec2:ModifySnapshotAttribute",
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "secretsmanager:GetSecretValue",
    "secretsmanager:ListSecrets",
    "ssm:GetParameter",
    "ssm:GetParameters",
    "ssm:GetParametersByPath",
    "kms:Decrypt",
    "kms:GenerateDataKey",
    "lambda:GetFunction",
    "codecommit:GitPull",
    "cloudtrail:StopLogging",
    "cloudtrail:DeleteTrail",
    "guardduty:DeleteDetector",
    "logs:DeleteLogGroup",
    "logs:DeleteLogStream",
]
@dataclass
class IAMFinding:
    """Represents a single IAM or cloud posture finding."""
    finding_id: str
    category: str               # privilege-escalation | data-exfil | public-exposure | s3 | sg
    severity: str               # critical | high | medium | low | informational
    title: str
    description: str
    affected_actions: List[str] = field(default_factory=list)
    affected_resource: str = "*"
    recommendation: str = ""
    mitre_technique: str = ""
@dataclass
class IAMAnalysisResult:
    """Aggregated result of an IAM / posture analysis run."""
    source: str
    check_mode: str
    provider: str
    severity_modifier: str
    findings: List[IAMFinding] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp_utc:
            self.timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "high")

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "medium")

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "low")
_SEV_LADDER = ["informational", "low", "medium", "high", "critical"]
def _bump_severity(severity: str, modifier: str) -> str:
    """
    Bump severity up one band when modifier is internet-facing or regulated-data.

    low -> medium -> high -> critical (caps at critical).
    """
    if modifier not in ("internet-facing", "regulated-data"):
        return severity
    try:
        idx = _SEV_LADDER.index(severity.lower())
        return _SEV_LADDER[min(idx + 1, len(_SEV_LADDER) - 1)]
    except ValueError:
        return severity
def _extract_actions(statement: dict) -> List[str]:
    """Normalise Action field to a list of lowercase strings."""
    action_field = statement.get("Action") or statement.get("action") or []
    if isinstance(action_field, str):
        return [action_field.lower()]
    return [str(a).lower() for a in action_field]
def _extract_resources(statement: dict) -> List[str]:
    """Normalise Resource field to a list of strings."""
    resource_field = (
        statement.get("Resource")
        or statement.get("resource")
        or ["*"]
    )
    if isinstance(resource_field, str):
        return [resource_field]
    return [str(r) for r in resource_field]
def _extract_principal(statement: dict) -> str:
    """Return a string representation of the Principal."""
    principal = statement.get("Principal") or statement.get("principal") or "N/A"
    if isinstance(principal, dict):
        parts = []
        for k, v in principal.items():
            if isinstance(v, list):
                parts.append(f"{k}:{','.join(v)}")
            else:
                parts.append(f"{k}:{v}")
        return " | ".join(parts)
    return str(principal)
def _is_allow(statement: dict) -> bool:
    effect = str(statement.get("Effect") or statement.get("effect") or "Allow")
    return effect.strip().lower() == "allow"

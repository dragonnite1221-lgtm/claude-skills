# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_security_scanner_base import *  # noqa: F403,E402


IAM_PATTERNS = [
    {
        "id": "SEC010",
        "name": "iam_wildcard_action",
        "severity": "critical",
        "pattern": r'Action\s*=\s*"\*"',
        "message": "IAM policy with wildcard Action = \"*\" — grants all permissions",
        "fix": "Scope Action to specific services and operations",
    },
    {
        "id": "SEC011",
        "name": "iam_wildcard_resource",
        "severity": "high",
        "pattern": r'Resource\s*=\s*"\*"',
        "message": "IAM policy with wildcard Resource = \"*\" — applies to all resources",
        "fix": "Scope Resource to specific ARN patterns",
    },
    {
        "id": "SEC012",
        "name": "iam_star_star",
        "severity": "critical",
        "pattern": r'Action\s*=\s*"\*"[^}]*Resource\s*=\s*"\*"',
        "message": "IAM policy with Action=* AND Resource=* — effectively admin access",
        "fix": "Follow least-privilege: grant only the specific actions and resources needed",
    },
]
NETWORK_PATTERNS = [
    {
        "id": "SEC020",
        "name": "sg_ssh_open",
        "severity": "critical",
        "pattern": None,  # Custom check
        "message": "Security group allows SSH (port 22) from 0.0.0.0/0",
        "fix": "Restrict to known CIDR blocks, or use SSM Session Manager instead",
    },
    {
        "id": "SEC021",
        "name": "sg_rdp_open",
        "severity": "critical",
        "pattern": None,  # Custom check
        "message": "Security group allows RDP (port 3389) from 0.0.0.0/0",
        "fix": "Restrict to known CIDR blocks, or use a bastion host",
    },
    {
        "id": "SEC022",
        "name": "sg_all_ports",
        "severity": "critical",
        "pattern": None,  # Custom check
        "message": "Security group allows all ports (0-65535) from 0.0.0.0/0",
        "fix": "Open only the specific ports your application needs",
    },
]
ENCRYPTION_PATTERNS = [
    {
        "id": "SEC030",
        "name": "s3_no_encryption",
        "severity": "high",
        "pattern": None,  # Custom check
        "message": "S3 bucket without server-side encryption configuration",
        "fix": "Add aws_s3_bucket_server_side_encryption_configuration resource",
    },
    {
        "id": "SEC031",
        "name": "rds_no_encryption",
        "severity": "high",
        "pattern": None,  # Custom check
        "message": "RDS instance without storage encryption",
        "fix": "Set storage_encrypted = true on aws_db_instance",
    },
    {
        "id": "SEC032",
        "name": "ebs_no_encryption",
        "severity": "medium",
        "pattern": None,  # Custom check
        "message": "EBS volume without encryption",
        "fix": "Set encrypted = true on aws_ebs_volume or enable account-level default encryption",
    },
]
ACCESS_PATTERNS = [
    {
        "id": "SEC040",
        "name": "rds_public",
        "severity": "high",
        "pattern": r'publicly_accessible\s*=\s*true',
        "message": "RDS instance is publicly accessible",
        "fix": "Set publicly_accessible = false and access via VPC/bastion",
    },
    {
        "id": "SEC041",
        "name": "s3_public_acl",
        "severity": "high",
        "pattern": r'acl\s*=\s*"public-read(?:-write)?"',
        "message": "S3 bucket with public ACL",
        "fix": "Remove public ACL and add aws_s3_bucket_public_access_block",
    },
]
def find_tf_files(directory):
    """Find all .tf files in a directory (non-recursive)."""
    tf_files = {}
    for entry in sorted(os.listdir(directory)):
        if entry.endswith(".tf"):
            filepath = os.path.join(directory, entry)
            with open(filepath, encoding="utf-8") as f:
                tf_files[entry] = f.read()
    return tf_files
def check_regex_rules(content, rules):
    """Run regex-based security rules against content."""
    findings = []
    for rule in rules:
        if rule["pattern"] is None:
            continue
        for match in re.finditer(rule["pattern"], content, re.MULTILINE | re.IGNORECASE):
            findings.append({
                "id": rule["id"],
                "severity": rule["severity"],
                "message": rule["message"],
                "fix": rule["fix"],
                "line": match.group(0).strip()[:80],
            })
    return findings

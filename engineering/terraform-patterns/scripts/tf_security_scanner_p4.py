# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_security_scanner_base import *  # noqa: F403,E402
# fmt: off
from tf_security_scanner_p2 import ENCRYPTION_PATTERNS  # noqa: E402,E501
# fmt: on


def check_encryption(content):
    """Custom check for missing encryption on storage resources."""
    findings = []

    # S3 buckets without encryption
    s3_buckets = re.findall(
        r'resource\s+"aws_s3_bucket"\s+"([^"]+)"', content
    )
    s3_encryption = re.findall(
        r'resource\s+"aws_s3_bucket_server_side_encryption_configuration"', content
    )
    # Also check inline encryption (older format)
    inline_encryption = re.findall(
        r'server_side_encryption_configuration', content
    )
    if s3_buckets and not s3_encryption and not inline_encryption:
        rule = next(r for r in ENCRYPTION_PATTERNS if r["id"] == "SEC030")
        for bucket in s3_buckets:
            findings.append({
                "id": rule["id"],
                "severity": rule["severity"],
                "message": f"{rule['message']} (bucket: {bucket})",
                "fix": rule["fix"],
                "line": f'aws_s3_bucket.{bucket}',
            })

    # RDS without encryption
    rds_blocks = re.finditer(
        r'resource\s+"aws_db_instance"\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    for rds_match in rds_blocks:
        name = rds_match.group(1)
        body = rds_match.group(2)
        if 'storage_encrypted' not in body or re.search(
            r'storage_encrypted\s*=\s*false', body
        ):
            rule = next(r for r in ENCRYPTION_PATTERNS if r["id"] == "SEC031")
            findings.append({
                "id": rule["id"],
                "severity": rule["severity"],
                "message": f"{rule['message']} (instance: {name})",
                "fix": rule["fix"],
                "line": f'aws_db_instance.{name}',
            })

    # EBS volumes without encryption
    ebs_blocks = re.finditer(
        r'resource\s+"aws_ebs_volume"\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    for ebs_match in ebs_blocks:
        name = ebs_match.group(1)
        body = ebs_match.group(2)
        if 'encrypted' not in body or re.search(
            r'encrypted\s*=\s*false', body
        ):
            rule = next(r for r in ENCRYPTION_PATTERNS if r["id"] == "SEC032")
            findings.append({
                "id": rule["id"],
                "severity": rule["severity"],
                "message": f"{rule['message']} (volume: {name})",
                "fix": rule["fix"],
                "line": f'aws_ebs_volume.{name}',
            })

    return findings
def check_sensitive_variables(content):
    """Check if variables that look like secrets are marked sensitive."""
    findings = []
    var_blocks = re.finditer(
        r'variable\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    secret_names = ["password", "secret", "token", "api_key", "private_key", "credentials"]

    for var_match in var_blocks:
        name = var_match.group(1)
        body = var_match.group(2)
        name_lower = name.lower()

        if any(s in name_lower for s in secret_names):
            if not re.search(r'sensitive\s*=\s*true', body):
                findings.append({
                    "id": "SEC050",
                    "severity": "medium",
                    "message": f"Variable '{name}' appears to be a secret but is not marked sensitive = true",
                    "fix": "Add sensitive = true to prevent the value from appearing in logs and plan output",
                    "line": f'variable "{name}"',
                })

            # Check for hardcoded default
            default_match = re.search(r'default\s*=\s*"([^"]+)"', body)
            if default_match and len(default_match.group(1)) > 0:
                findings.append({
                    "id": "SEC051",
                    "severity": "critical",
                    "message": f"Variable '{name}' has a hardcoded default value for a secret",
                    "fix": "Remove the default value — require it to be passed at runtime via tfvars or env",
                    "line": f'variable "{name}" default = "{default_match.group(1)[:20]}..."',
                })

    return findings

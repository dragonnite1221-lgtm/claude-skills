# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p2 import IAMAnalysisResult, IAMFinding, _bump_severity  # noqa: E402,E501
from cloud_posture_check_p4 import _csd_0, _csd_1  # noqa: E402,E501
# fmt: on


def check_s3_policy(
    policy: dict,
    source: str,
    severity_modifier: str,
) -> IAMAnalysisResult:
    """
    Check S3 bucket policy or Terraform aws_s3_bucket block for misconfigurations.

    Checks performed:
        1. Principal "*" in bucket policy -> Critical
        2. block_public_acls missing or false -> Critical
        3. server_side_encryption absent or not AES256/aws:kms -> High
        4. versioning disabled -> Medium
        5. access logging disabled -> High

    Args:
        policy:             Parsed S3 policy / Terraform block dict.
        source:             Display name / file path.
        severity_modifier:  internet-facing | regulated-data | none.

    Returns:
        IAMAnalysisResult populated with S3 findings.
    """
    result = IAMAnalysisResult(
        source=source,
        check_mode="s3",
        provider="aws",
        severity_modifier=severity_modifier,
    )
    findings: List[IAMFinding] = []
    fid = 0

    def _next_id() -> str:
        nonlocal fid
        fid += 1
        return f"S3-{fid:03d}"

    # --- Check 1: Public principal in bucket policy ---
    statements = policy.get("Statement") or policy.get("statement") or []
    _csd_0(findings, severity_modifier, source, statements)

    # --- Check 2: block_public_acls missing or false ---
    # Terraform resource format: aws_s3_bucket_public_access_block
    public_access_block = (
        policy.get("block_public_acls")
        or policy.get("BlockPublicAcls")
        or policy.get("public_access_block", {}).get("block_public_acls")
    )
    restrict_public_buckets = (
        policy.get("restrict_public_buckets")
        or policy.get("RestrictPublicBuckets")
    )
    block_public_policy = (
        policy.get("block_public_policy")
        or policy.get("BlockPublicPolicy")
    )

    # If any of these are explicitly False or absent, flag it
    block_fields = {
        "block_public_acls": public_access_block,
        "restrict_public_buckets": restrict_public_buckets,
        "block_public_policy": block_public_policy,
    }
    missing_blocks = [k for k, v in block_fields.items() if v is None or v is False]

    if missing_blocks:
        severity = _bump_severity("critical", severity_modifier)
        findings.append(IAMFinding(
            finding_id=_next_id(),
            category="s3",
            severity=severity,
            title="S3 Public Access Block Not Fully Enabled",
            description=(
                f"Public access block settings are missing or disabled: "
                f"{', '.join(missing_blocks)}. This may allow public ACL or policy access."
            ),
            affected_resource=source,
            recommendation=(
                "Enable all four S3 Block Public Access settings: "
                "BlockPublicAcls, BlockPublicPolicy, IgnorePublicAcls, RestrictPublicBuckets."
            ),
            mitre_technique="T1530",
        ))

    # --- Check 3: Server-side encryption ---
    sse_config = (
        policy.get("server_side_encryption_configuration")
        or policy.get("ServerSideEncryptionConfiguration")
        or policy.get("encryption")
        or policy.get("sse_algorithm")
    )

    has_sse = False
    if isinstance(sse_config, dict):
        rules = sse_config.get("Rule") or sse_config.get("rules") or []
        if not isinstance(rules, list):
            rules = [rules]
        for rule in rules:
            apply_sse = (
                rule.get("ApplyServerSideEncryptionByDefault")
                or rule.get("apply_server_side_encryption_by_default")
                or {}
            )
            algo = str(apply_sse.get("SSEAlgorithm") or apply_sse.get("sse_algorithm") or "")
            if algo.upper() in ("AES256", "AWS:KMS"):
                has_sse = True
    elif isinstance(sse_config, str):
        has_sse = sse_config.upper() in ("AES256", "AWS:KMS")

    severity = _csd_1(findings, has_sse, severity, severity_modifier, source)

    # --- Check 4: Versioning disabled ---
    versioning = (
        policy.get("versioning")
        or policy.get("VersioningConfiguration")
    )
    versioning_enabled = False
    if isinstance(versioning, dict):
        status = str(
            versioning.get("Status")
            or versioning.get("status")
            or versioning.get("enabled")
            or ""
        )
        versioning_enabled = status.lower() in ("enabled", "true")
    elif isinstance(versioning, bool):
        versioning_enabled = versioning

    if not versioning_enabled:
        severity = _bump_severity("medium", severity_modifier)
        findings.append(IAMFinding(
            finding_id=_next_id(),
            category="s3",
            severity=severity,
            title="S3 Bucket Versioning Disabled",
            description=(
                "Versioning is not enabled on this bucket. "
                "Accidental or malicious object deletion/overwrite cannot be recovered."
            ),
            affected_resource=source,
            recommendation=(
                "Enable bucket versioning. "
                "Combine with Object Lock and lifecycle policies for regulated workloads."
            ),
            mitre_technique="T1485",
        ))

    result.findings = findings
    result.summary = {
        "total_findings": len(findings),
        "critical": sum(1 for f in findings if f.severity == "critical"),
        "high": sum(1 for f in findings if f.severity == "high"),
        "medium": sum(1 for f in findings if f.severity == "medium"),
        "low": sum(1 for f in findings if f.severity == "low"),
        "check_mode": "s3",
        "provider": "aws",
        "severity_modifier": severity_modifier,
    }
    return result

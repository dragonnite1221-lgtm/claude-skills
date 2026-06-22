# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p2 import IAMAnalysisResult, IAMFinding, _bump_severity, _extract_actions, _extract_principal, _is_allow  # noqa: E402,E501
from cloud_posture_check_p3 import analyze_statement  # noqa: E402,E501
# fmt: on


def analyze_policy(
    policy: dict,
    check_mode: str,
    source: str,
    severity_modifier: str,
    provider: str = "aws",
) -> IAMAnalysisResult:
    """
    Analyse a full IAM policy document for findings.

    Iterates over every Statement in the policy and delegates to
    analyze_statement() for per-check logic.

    Args:
        policy:             Parsed IAM policy JSON dict.
        check_mode:         privilege-escalation | data-exfil | public-exposure.
        source:             Display name / file path for the policy.
        severity_modifier:  internet-facing | regulated-data | none.
        provider:           aws | azure | gcp (currently only aws fully supported).

    Returns:
        IAMAnalysisResult with all findings populated.
    """
    result = IAMAnalysisResult(
        source=source,
        check_mode=check_mode,
        provider=provider,
        severity_modifier=severity_modifier,
    )

    statements = policy.get("Statement") or policy.get("statement") or []
    if not isinstance(statements, list):
        statements = [statements]

    prefix = source.replace(" ", "_").replace("/", "_")[:12].upper()

    for idx, stmt in enumerate(statements):
        stmt_findings = analyze_statement(
            statement=stmt,
            check_mode=check_mode,
            finding_prefix=f"{prefix}-S{idx + 1:02d}",
            severity_modifier=severity_modifier,
        )
        result.findings.extend(stmt_findings)

    result.summary = {
        "total_statements": len(statements),
        "total_findings": len(result.findings),
        "critical": result.critical_count,
        "high": result.high_count,
        "medium": result.medium_count,
        "low": result.low_count,
        "check_mode": check_mode,
        "provider": provider,
        "severity_modifier": severity_modifier,
    }

    return result
def _csd_0(findings, severity_modifier, source, statements):
    if isinstance(statements, list):
        for stmt in statements:
            if not _is_allow(stmt):
                continue
            principal = _extract_principal(stmt)
            if "*" in principal or '"*"' in principal:
                severity = _bump_severity("critical", severity_modifier)
                findings.append(IAMFinding(
                    finding_id=_next_id(),
                    category="s3",
                    severity=severity,
                    title="S3 Bucket Policy: Public Principal",
                    description=(
                        "Bucket policy contains Principal '*' which grants public "
                        "access to any AWS account or unauthenticated user."
                    ),
                    affected_actions=_extract_actions(stmt),
                    affected_resource=source,
                    recommendation=(
                        "Remove Principal '*'. Restrict to specific account ARNs or "
                        "use aws:PrincipalOrgID condition to limit to your AWS Org."
                    ),
                    mitre_technique="T1530",
                ))
def _csd_1(findings, has_sse, severity, severity_modifier, source):
    if not has_sse:
        severity = _bump_severity("high", severity_modifier)
        findings.append(IAMFinding(
            finding_id=_next_id(),
            category="s3",
            severity=severity,
            title="S3 Server-Side Encryption Not Configured",
            description=(
                "No server-side encryption (SSE-S3 or SSE-KMS) found on this bucket. "
                "Data is stored unencrypted at rest."
            ),
            affected_resource=source,
            recommendation=(
                "Enable SSE via a bucket encryption configuration. "
                "Use aws:kms with a CMK for regulated workloads. "
                "Consider enforcing encryption via bucket policy (aws:SecureTransport)."
            ),
            mitre_technique="T1022",
        ))
    return severity

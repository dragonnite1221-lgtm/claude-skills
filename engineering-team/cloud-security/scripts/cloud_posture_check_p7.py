# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p2 import IAMAnalysisResult  # noqa: E402,E501
from cloud_posture_check_p4 import analyze_policy  # noqa: E402,E501
from cloud_posture_check_p5 import check_s3_policy  # noqa: E402,E501
from cloud_posture_check_p6 import check_security_group  # noqa: E402,E501
# fmt: on


def print_text_report(result: IAMAnalysisResult) -> None:
    """Print a formatted text report for the analysis result."""
    sep = "=" * 70
    print(sep)
    print("  Cloud Posture Check")
    print(sep)
    print(f"  Source          : {result.source}")
    print(f"  Check Mode      : {result.check_mode}")
    print(f"  Provider        : {result.provider.upper()}")
    print(f"  Severity Mod    : {result.severity_modifier}")
    print(f"  Timestamp       : {result.timestamp_utc}")
    print(sep)

    summary = result.summary
    print(f"\n  Summary:")
    print(f"    Total Findings  : {summary.get('total_findings', 0)}")
    if summary.get("critical", 0):
        print(f"    CRITICAL        : {summary['critical']}")
    if summary.get("high", 0):
        print(f"    HIGH            : {summary['high']}")
    if summary.get("medium", 0):
        print(f"    MEDIUM          : {summary['medium']}")
    if summary.get("low", 0):
        print(f"    LOW             : {summary['low']}")

    if not result.findings:
        print("\n  No findings detected.")
        print(sep)
        return

    print(f"\n  Findings ({len(result.findings)}):")
    for finding in result.findings:
        print(f"\n  [{finding.severity.upper()}] {finding.finding_id}: {finding.title}")
        print(f"    {finding.description}")
        if finding.affected_actions:
            preview = finding.affected_actions[:4]
            suffix = f" (+{len(finding.affected_actions) - 4} more)" if len(finding.affected_actions) > 4 else ""
            print(f"    Actions  : {', '.join(preview)}{suffix}")
        print(f"    Resource : {finding.affected_resource}")
        print(f"    MITRE    : {finding.mitre_technique}")
        print(f"    Fix      : {finding.recommendation}")

    print(f"\n{sep}")
def result_to_dict(result: IAMAnalysisResult) -> dict:
    """Convert IAMAnalysisResult to a JSON-serialisable dict."""
    return {
        "source": result.source,
        "check_mode": result.check_mode,
        "provider": result.provider,
        "severity_modifier": result.severity_modifier,
        "timestamp_utc": result.timestamp_utc,
        "summary": result.summary,
        "findings": [asdict(f) for f in result.findings],
    }
def _csd_2(all_results, check_mode, iam_check_modes, policy_data, provider, severity_modifier, source):
    if check_mode == "all":
        if provider == "aws":
            # Run all IAM checks
            for mode in iam_check_modes:
                r = analyze_policy(
                    policy=policy_data,
                    check_mode=mode,
                    source=source,
                    severity_modifier=severity_modifier,
                    provider=provider,
                )
                all_results.append(r)
            # Run S3
            s3_r = check_s3_policy(
                policy=policy_data,
                source=source,
                severity_modifier=severity_modifier,
            )
            all_results.append(s3_r)
            # Run SG
            sg_r = check_security_group(
                sg_json=policy_data,
                source=source,
                severity_modifier=severity_modifier,
            )
            all_results.append(sg_r)
        else:
            for mode in iam_check_modes:
                r = analyze_policy(
                    policy=policy_data,
                    check_mode=mode,
                    source=source,
                    severity_modifier=severity_modifier,
                    provider=provider,
                )
                all_results.append(r)

    elif check_mode in iam_check_modes:
        r = analyze_policy(
            policy=policy_data,
            check_mode=check_mode,
            source=source,
            severity_modifier=severity_modifier,
            provider=provider,
        )
        all_results.append(r)

    elif check_mode == "s3":
        r = check_s3_policy(
            policy=policy_data,
            source=source,
            severity_modifier=severity_modifier,
        )
        all_results.append(r)

    elif check_mode == "sg":
        r = check_security_group(
            sg_json=policy_data,
            source=source,
            severity_modifier=severity_modifier,
        )
        all_results.append(r)
    return r

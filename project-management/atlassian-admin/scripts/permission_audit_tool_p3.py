# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from permission_audit_tool_base import *  # noqa: F403,E402
# fmt: off
from permission_audit_tool_p1 import SEVERITY_WEIGHTS, check_direct_user_permissions, check_over_permissioned_groups  # noqa: E402,E501
from permission_audit_tool_p2 import check_compliance_gaps, check_missing_restrictions, check_scheme_consistency  # noqa: E402,E501
# fmt: on


def _generate_remediations(findings: List[Dict[str, str]]) -> List[str]:
    """Generate remediation recommendations."""
    remediations = []
    rules_seen = set()

    for finding in findings:
        rule = finding["rule"]
        if rule in rules_seen:
            continue
        rules_seen.add(rule)

        if rule == "over_permissioned_group":
            remediations.append("Review and reduce sensitive permissions for over-permissioned groups. Apply principle of least privilege.")
        elif rule == "admin_access_warning":
            remediations.append("Audit admin group membership. Limit system/Jira admin access to essential personnel only.")
        elif rule == "direct_user_permission":
            remediations.append("Migrate direct user permissions to group-based grants. Create functional groups for common permission sets.")
        elif rule == "unrestricted_delete":
            remediations.append("Restrict delete permissions to project admins or leads. Remove from broad user groups.")
        elif rule == "scheme_inconsistency":
            remediations.append("Standardize permission schemes across projects. Document intentional differences.")
        elif rule == "too_many_direct_users":
            remediations.append("Create groups for users with direct permissions. This simplifies onboarding/offboarding.")
        elif rule == "separation_of_duties":
            remediations.append("Consider splitting admin responsibilities across multiple groups for better separation of duties.")
        elif rule == "no_admin_defined":
            remediations.append("Define explicit admin permissions in each scheme to ensure proper project governance.")

    return remediations
def audit_permissions(data: Dict[str, Any]) -> Dict[str, Any]:
    """Run full permission audit."""
    schemes = data.get("schemes", [])

    if not schemes:
        # Try treating the entire input as a single scheme
        if data.get("grants") or data.get("name"):
            schemes = [data]
        else:
            return {
                "risk_score": 0,
                "grade": "invalid",
                "error": "No permission schemes found in input",
                "findings": [],
                "summary": {},
            }

    all_findings = []
    all_findings.extend(check_over_permissioned_groups(schemes))
    all_findings.extend(check_direct_user_permissions(schemes))
    all_findings.extend(check_missing_restrictions(schemes))
    all_findings.extend(check_scheme_consistency(schemes))
    all_findings.extend(check_compliance_gaps(schemes))

    # Calculate risk score (higher = more risk)
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    total_penalty = 0
    for finding in all_findings:
        severity = finding["severity"]
        summary[severity] = summary.get(severity, 0) + 1
        total_penalty += SEVERITY_WEIGHTS.get(severity, 0)

    risk_score = min(100, total_penalty)
    health_score = max(0, 100 - risk_score)

    if health_score >= 85:
        grade = "excellent"
    elif health_score >= 70:
        grade = "good"
    elif health_score >= 50:
        grade = "fair"
    else:
        grade = "poor"

    # Generate remediation recommendations
    remediations = _generate_remediations(all_findings)

    return {
        "risk_score": risk_score,
        "health_score": health_score,
        "grade": grade,
        "schemes_analyzed": len(schemes),
        "findings": all_findings,
        "summary": summary,
        "remediations": remediations,
    }

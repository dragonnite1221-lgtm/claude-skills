# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p1 import ESCALATION_COMBOS, PRIVILEGE_ESCALATION_ACTIONS  # noqa: E402,E501
from cloud_posture_check_p2 import DATA_EXFILTRATION_ACTIONS, IAMFinding, _bump_severity, _extract_actions, _extract_principal, _extract_resources, _is_allow  # noqa: E402,E501
# fmt: on


def analyze_statement(
    statement: dict,
    check_mode: str,
    finding_prefix: str,
    severity_modifier: str,
) -> List[IAMFinding]:
    """
    Analyse a single IAM policy statement for risks.

    Args:
        statement:          Parsed IAM statement dict.
        check_mode:         One of privilege-escalation | data-exfil | public-exposure.
        finding_prefix:     Short string used to prefix finding IDs.
        severity_modifier:  internet-facing | regulated-data | none.

    Returns:
        List of IAMFinding objects (may be empty).
    """
    findings: List[IAMFinding] = []

    if not _is_allow(statement):
        return findings

    actions = _extract_actions(statement)
    resources = _extract_resources(statement)
    principal = _extract_principal(statement)
    resource_str = ", ".join(resources[:3]) + ("..." if len(resources) > 3 else "")

    wildcard_resource = any(r in ("*", "arn:aws:*") for r in resources)
    wildcard_action = any(a in ("*", "iam:*", "s3:*", "ec2:*") for a in actions)

    if check_mode == "privilege-escalation":
        # Check individual high-risk actions
        matched_privesc = [
            a for a in actions
            if a in [p.lower() for p in PRIVILEGE_ESCALATION_ACTIONS]
        ]

        if matched_privesc:
            severity = "high" if not wildcard_resource else "critical"
            severity = _bump_severity(severity, severity_modifier)
            findings.append(IAMFinding(
                finding_id=f"{finding_prefix}-PRIVESC-{len(findings) + 1:03d}",
                category="privilege-escalation",
                severity=severity,
                title="Privilege Escalation Actions Detected",
                description=(
                    f"Statement grants {len(matched_privesc)} privilege escalation "
                    f"action(s) to principal '{principal}' on resources: {resource_str}."
                ),
                affected_actions=matched_privesc,
                affected_resource=resource_str,
                recommendation=(
                    "Apply least-privilege: restrict IAM mutation actions to specific "
                    "resource ARNs and add Condition constraints. Consider permission boundaries."
                ),
                mitre_technique="T1098",
            ))

        # Check dangerous combos
        for combo in ESCALATION_COMBOS:
            combo_actions_lower = [c.lower() for c in combo["actions"]]
            if all(ca in actions for ca in combo_actions_lower):
                combo_sev = _bump_severity(combo["severity"], severity_modifier)
                findings.append(IAMFinding(
                    finding_id=f"{finding_prefix}-COMBO-{len(findings) + 1:03d}",
                    category="privilege-escalation",
                    severity=combo_sev,
                    title=f"Escalation Combo: {combo['name']}",
                    description=combo["description"],
                    affected_actions=combo["actions"],
                    affected_resource=resource_str,
                    recommendation=(
                        f"Remove or scope one of the combo actions. "
                        f"Separate {combo['name']} permissions across different roles."
                    ),
                    mitre_technique="T1548",
                ))

        # Wildcard action with Allow
        if wildcard_action:
            sev = _bump_severity("critical", severity_modifier)
            findings.append(IAMFinding(
                finding_id=f"{finding_prefix}-WILD-{len(findings) + 1:03d}",
                category="privilege-escalation",
                severity=sev,
                title="Wildcard Action Grant",
                description=(
                    f"Statement uses wildcard action(s) {[a for a in actions if '*' in a]} "
                    f"for principal '{principal}'. This grants unrestricted access."
                ),
                affected_actions=[a for a in actions if "*" in a],
                affected_resource=resource_str,
                recommendation="Replace wildcard actions with an explicit allowlist of required actions.",
                mitre_technique="T1078.004",
            ))

    elif check_mode == "data-exfil":
        matched_exfil = [
            a for a in actions
            if a in [d.lower() for d in DATA_EXFILTRATION_ACTIONS]
        ]

        if matched_exfil:
            severity = "medium"
            if wildcard_resource:
                severity = "high"
            # Particularly dangerous: log deletion or trail stopping
            disruptive = [
                a for a in matched_exfil
                if any(x in a for x in ["stoplog", "deletelog", "deletetrail", "deletedetector"])
            ]
            if disruptive:
                severity = "critical"
            severity = _bump_severity(severity, severity_modifier)

            findings.append(IAMFinding(
                finding_id=f"{finding_prefix}-EXFIL-{len(findings) + 1:03d}",
                category="data-exfil",
                severity=severity,
                title="Data Exfiltration Risk Actions",
                description=(
                    f"Statement grants {len(matched_exfil)} potential exfiltration "
                    f"action(s) to principal '{principal}': {', '.join(matched_exfil[:5])}."
                ),
                affected_actions=matched_exfil,
                affected_resource=resource_str,
                recommendation=(
                    "Scope data-read actions to specific resource ARNs. "
                    "Add VPC endpoint conditions and restrict cross-account access. "
                    "Enable GuardDuty and CloudTrail for all regions."
                ),
                mitre_technique="T1530",
            ))

    elif check_mode == "public-exposure":
        principal_str = _extract_principal(statement)
        is_public = any(p in principal_str for p in ["*", "AWS:*", '"*"'])

        if is_public:
            sev = _bump_severity("high", severity_modifier)
            if wildcard_action:
                sev = _bump_severity("critical", severity_modifier)

            findings.append(IAMFinding(
                finding_id=f"{finding_prefix}-PUB-{len(findings) + 1:03d}",
                category="public-exposure",
                severity=sev,
                title="Public Principal Detected",
                description=(
                    f"Statement uses Principal '*' allowing any AWS account or "
                    f"unauthenticated entity to perform: {', '.join(actions[:5])}."
                ),
                affected_actions=actions[:10],
                affected_resource=resource_str,
                recommendation=(
                    "Replace Principal '*' with specific account ARNs, "
                    "organisation units, or role ARNs. Use Condition keys "
                    "like aws:PrincipalOrgID to limit to your AWS Org."
                ),
                mitre_technique="T1190",
            ))

    return findings

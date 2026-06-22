# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from permission_audit_tool_base import *  # noqa: F403,E402
# fmt: off
from permission_audit_tool_p1 import SENSITIVE_PERMISSIONS  # noqa: E402,E501
# fmt: on


def check_missing_restrictions(
    schemes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Check for missing restrictions on sensitive actions."""
    findings = []

    for scheme in schemes:
        scheme_name = scheme.get("name", "Unknown Scheme")
        grants = scheme.get("grants", [])

        granted_permissions = set()
        for grant in grants:
            granted_permissions.add(grant.get("permission", "").lower())

        # Check if delete permissions are unrestricted
        delete_perms = {"delete_issues", "delete_all_comments", "delete_all_attachments"}
        unrestricted_deletes = delete_perms & granted_permissions

        for grant in grants:
            perm = grant.get("permission", "").lower()
            group = grant.get("group", "")
            if perm in delete_perms and group:
                # Check if granted to broad groups
                broad_groups = {"users", "everyone", "all-users", "jira-users", "jira-software-users"}
                if group.lower() in broad_groups:
                    findings.append({
                        "rule": "unrestricted_delete",
                        "severity": "critical",
                        "scheme": scheme_name,
                        "message": f"Delete permission '{perm}' granted to broad group '{group}' "
                                   f"in '{scheme_name}'. Restrict to admins or leads only.",
                    })

        # Check if admin permissions exist
        admin_perms = {"administer_project", "administer_jira", "system_admin"}
        if not (admin_perms & granted_permissions):
            findings.append({
                "rule": "no_admin_defined",
                "severity": "medium",
                "scheme": scheme_name,
                "message": f"No explicit admin permission defined in '{scheme_name}'. "
                           f"Ensure project administration is properly assigned.",
            })

    return findings
def check_scheme_consistency(
    schemes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Check for inconsistencies across permission schemes."""
    findings = []

    if len(schemes) < 2:
        return findings

    # Compare permission sets across schemes
    scheme_perms = {}
    for scheme in schemes:
        name = scheme.get("name", "Unknown")
        perms = set()
        for grant in scheme.get("grants", []):
            perms.add(grant.get("permission", "").lower())
        scheme_perms[name] = perms

    # Find schemes with significantly different permission sets
    all_perms = set()
    for perms in scheme_perms.values():
        all_perms |= perms

    scheme_names = list(scheme_perms.keys())
    for i in range(len(scheme_names)):
        for j in range(i + 1, len(scheme_names)):
            name_a = scheme_names[i]
            name_b = scheme_names[j]
            diff = scheme_perms[name_a].symmetric_difference(scheme_perms[name_b])
            if len(diff) > 5:
                findings.append({
                    "rule": "scheme_inconsistency",
                    "severity": "medium",
                    "message": f"Schemes '{name_a}' and '{name_b}' differ significantly "
                               f"({len(diff)} different permissions). Review for intentional differences.",
                })

    return findings
def check_compliance_gaps(
    schemes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Check for common compliance gaps."""
    findings = []

    for scheme in schemes:
        scheme_name = scheme.get("name", "Unknown Scheme")
        grants = scheme.get("grants", [])

        groups_used = set()
        users_used = set()
        for grant in grants:
            if grant.get("group"):
                groups_used.add(grant["group"])
            if grant.get("user"):
                users_used.add(grant["user"])

        # Check for separation of duties
        admin_groups = set()
        for grant in grants:
            if grant.get("permission", "").lower() in SENSITIVE_PERMISSIONS and grant.get("group"):
                admin_groups.add(grant["group"])

        if len(admin_groups) == 1 and len(groups_used) > 1:
            findings.append({
                "rule": "separation_of_duties",
                "severity": "info",
                "scheme": scheme_name,
                "message": f"Only one group ('{next(iter(admin_groups))}') holds all sensitive permissions "
                           f"in '{scheme_name}'. Consider separating duties across multiple groups.",
            })

        # Check user count
        if len(users_used) > 5:
            findings.append({
                "rule": "too_many_direct_users",
                "severity": "high",
                "scheme": scheme_name,
                "message": f"Scheme '{scheme_name}' has {len(users_used)} direct user grants. "
                           f"Migrate to group-based permissions for better governance.",
            })

    return findings

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from permission_audit_tool_base import *  # noqa: F403,E402


SENSITIVE_PERMISSIONS = {
    "administer_project",
    "administer_jira",
    "delete_issues",
    "delete_all_comments",
    "delete_all_attachments",
    "manage_watchers",
    "modify_reporter",
    "bulk_change",
    "system_admin",
    "manage_group_filter_subscriptions",
}
RECOMMENDED_GROUP_ONLY_PERMISSIONS = {
    "browse_projects",
    "create_issues",
    "edit_issues",
    "transition_issues",
    "assign_issues",
    "resolve_issues",
    "close_issues",
    "add_comments",
    "edit_all_comments",
}
SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "info": 1,
}
def check_over_permissioned_groups(
    schemes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Check for groups with overly broad admin access."""
    findings = []

    for scheme in schemes:
        scheme_name = scheme.get("name", "Unknown Scheme")
        grants = scheme.get("grants", [])

        group_permissions = {}
        for grant in grants:
            group = grant.get("group", "")
            permission = grant.get("permission", "").lower()
            if group:
                if group not in group_permissions:
                    group_permissions[group] = set()
                group_permissions[group].add(permission)

        for group, perms in group_permissions.items():
            admin_perms = perms & SENSITIVE_PERMISSIONS
            if len(admin_perms) >= 3:
                findings.append({
                    "rule": "over_permissioned_group",
                    "severity": "high",
                    "scheme": scheme_name,
                    "group": group,
                    "message": f"Group '{group}' has {len(admin_perms)} sensitive permissions "
                               f"in scheme '{scheme_name}': {', '.join(sorted(admin_perms))}. "
                               f"Review if all are necessary.",
                })

            if "system_admin" in perms or "administer_jira" in perms:
                findings.append({
                    "rule": "admin_access_warning",
                    "severity": "critical",
                    "scheme": scheme_name,
                    "group": group,
                    "message": f"Group '{group}' has system/Jira admin access in '{scheme_name}'. "
                               f"Ensure this is strictly necessary and membership is limited.",
                })

    return findings
def check_direct_user_permissions(
    schemes: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Check for permissions granted directly to users instead of groups."""
    findings = []

    for scheme in schemes:
        scheme_name = scheme.get("name", "Unknown Scheme")
        grants = scheme.get("grants", [])

        for grant in grants:
            user = grant.get("user", "")
            permission = grant.get("permission", "")

            if user and not grant.get("group"):
                severity = "high" if permission.lower() in SENSITIVE_PERMISSIONS else "medium"
                findings.append({
                    "rule": "direct_user_permission",
                    "severity": severity,
                    "scheme": scheme_name,
                    "user": user,
                    "message": f"User '{user}' has direct permission '{permission}' in '{scheme_name}'. "
                               f"Use groups instead for maintainability and audit clarity.",
                })

    return findings

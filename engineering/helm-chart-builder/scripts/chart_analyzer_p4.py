# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402
# fmt: off
from chart_analyzer_p1 import SECURITY_CHECKS  # noqa: E402,E501
# fmt: on


def check_security(chart_dir):
    """Run security-focused checks."""
    findings = []
    templates_dir = chart_dir / "templates"
    if not templates_dir.exists():
        return findings

    template_files = list(templates_dir.glob("*.yaml")) + list(templates_dir.glob("*.yml"))
    all_content = ""
    for tpl_file in template_files:
        all_content += tpl_file.read_text(encoding="utf-8") + "\n"

    for check in SECURITY_CHECKS:
        triggered = False

        if check["check"] == "no_security_context":
            if "securityContext" not in all_content and template_files:
                triggered = True
        elif check["check"] == "privileged_container":
            if re.search(r"privileged:\s*true", all_content):
                triggered = True
        elif check["check"] == "no_run_as_non_root":
            if "securityContext" in all_content and "runAsNonRoot" not in all_content:
                triggered = True
        elif check["check"] == "no_readonly_rootfs":
            if "securityContext" in all_content and "readOnlyRootFilesystem" not in all_content:
                triggered = True
        elif check["check"] == "no_network_policy":
            np_file = templates_dir / "networkpolicy.yaml"
            if not np_file.exists() and "NetworkPolicy" not in all_content:
                triggered = True
        elif check["check"] == "automount_sa_token":
            if "automountServiceAccountToken" not in all_content and template_files:
                triggered = True
        elif check["check"] == "host_network":
            if re.search(r"hostNetwork:\s*true", all_content):
                triggered = True
        elif check["check"] == "host_pid_ipc":
            if re.search(r"host(?:PID|IPC):\s*true", all_content):
                triggered = True

        if triggered:
            findings.append({
                "id": check["id"],
                "severity": check["severity"],
                "message": check["message"],
                "fix": check["fix"],
                "file": "templates/",
            })

    # Check for secrets in values.yaml
    values_path = chart_dir / "values.yaml"
    if values_path.exists():
        values_content = values_path.read_text(encoding="utf-8")
        for match in re.finditer(r"^(\s*\S*(?:password|secret|token|apiKey|api_key)\s*:\s*)(\S+)", values_content, re.MULTILINE | re.IGNORECASE):
            val = match.group(2).strip("'\"")
            if val and val not in ("null", "~", '""', "''", "changeme", "CHANGEME", "TODO"):
                findings.append({
                    "id": "SC009",
                    "severity": "critical",
                    "message": f"Potential secret in values.yaml default: {match.group(0).strip()[:60]}",
                    "fix": "Remove default secret values. Use empty string or null with documentation",
                    "file": "values.yaml",
                    "line": match.group(0).strip()[:80],
                })

    return findings

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402


REQUIRED_FILES = [
    {"path": "Chart.yaml", "severity": "critical", "message": "Missing Chart.yaml — not a valid Helm chart"},
    {"path": "values.yaml", "severity": "high", "message": "Missing values.yaml — chart has no configurable defaults"},
    {"path": "templates/_helpers.tpl", "severity": "high", "message": "Missing _helpers.tpl — no shared label/name helpers"},
    {"path": "templates/NOTES.txt", "severity": "medium", "message": "Missing NOTES.txt — no post-install instructions for users"},
    {"path": ".helmignore", "severity": "low", "message": "Missing .helmignore — CI files, .git, tests may be packaged"},
]
CHART_YAML_CHECKS = [
    {"field": "apiVersion", "severity": "critical", "message": "Missing apiVersion in Chart.yaml"},
    {"field": "name", "severity": "critical", "message": "Missing name in Chart.yaml"},
    {"field": "version", "severity": "critical", "message": "Missing version in Chart.yaml"},
    {"field": "description", "severity": "medium", "message": "Missing description in Chart.yaml"},
    {"field": "appVersion", "severity": "medium", "message": "Missing appVersion in Chart.yaml — operators won't know what app version is deployed"},
    {"field": "type", "severity": "low", "message": "Missing type in Chart.yaml — defaults to 'application'"},
]
TEMPLATE_ANTI_PATTERNS = [
    {
        "id": "TP001",
        "severity": "high",
        "pattern": r'image:\s*["\']?[a-z][a-z0-9./-]+:[a-z0-9][a-z0-9._-]*["\']?\s*$',
        "message": "Hardcoded image tag in template — must use .Values.image.repository and .Values.image.tag",
        "fix": 'Use: image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"',
    },
    {
        "id": "TP002",
        "severity": "high",
        "pattern": r'replicas:\s*\d+\s*$',
        "message": "Hardcoded replica count — must be configurable via values",
        "fix": "Use: replicas: {{ .Values.replicaCount }}",
    },
    {
        "id": "TP003",
        "severity": "medium",
        "pattern": r'port:\s*\d+\s*$',
        "message": "Hardcoded port number — should be configurable via values",
        "fix": "Use: port: {{ .Values.service.port }}",
    },
    {
        "id": "TP004",
        "severity": "high",
        "pattern": r'(?:name|namespace):\s*[a-z][a-z0-9-]+\s*$',
        "message": "Hardcoded name/namespace — should use template helpers",
        "fix": 'Use: name: {{ include "mychart.fullname" . }}',
    },
    {
        "id": "TP005",
        "severity": "medium",
        "pattern": r'nodePort:\s*\d+',
        "message": "Hardcoded nodePort — should be configurable or avoided",
        "fix": "Use: nodePort: {{ .Values.service.nodePort }} with conditional",
    },
]
SECURITY_CHECKS = [
    {
        "id": "SC001",
        "severity": "critical",
        "check": "no_security_context",
        "message": "No securityContext found in any template — pods run as root with full capabilities",
        "fix": "Add pod and container securityContext with runAsNonRoot, readOnlyRootFilesystem, drop ALL capabilities",
    },
    {
        "id": "SC002",
        "severity": "critical",
        "check": "privileged_container",
        "message": "Privileged container detected — full host access",
        "fix": "Remove privileged: true. Use specific capabilities instead",
    },
    {
        "id": "SC003",
        "severity": "high",
        "check": "no_run_as_non_root",
        "message": "No runAsNonRoot: true — container may run as root",
        "fix": "Add runAsNonRoot: true to pod securityContext",
    },
    {
        "id": "SC004",
        "severity": "high",
        "check": "no_readonly_rootfs",
        "message": "No readOnlyRootFilesystem — container filesystem is writable",
        "fix": "Add readOnlyRootFilesystem: true and use emptyDir for writable paths",
    },
    {
        "id": "SC005",
        "severity": "medium",
        "check": "no_network_policy",
        "message": "No NetworkPolicy template — all pod-to-pod traffic allowed",
        "fix": "Add a NetworkPolicy template with default-deny ingress and explicit allow rules",
    },
    {
        "id": "SC006",
        "severity": "medium",
        "check": "automount_sa_token",
        "message": "automountServiceAccountToken not set to false — pod can access K8s API",
        "fix": "Set automountServiceAccountToken: false unless the pod needs K8s API access",
    },
    {
        "id": "SC007",
        "severity": "high",
        "check": "host_network",
        "message": "hostNetwork: true — pod shares host network namespace",
        "fix": "Remove hostNetwork unless absolutely required (e.g., CNI plugin)",
    },
    {
        "id": "SC008",
        "severity": "critical",
        "check": "host_pid_ipc",
        "message": "hostPID or hostIPC enabled — pod can see host processes/IPC",
        "fix": "Remove hostPID and hostIPC — never needed in application charts",
    },
]
LABEL_PATTERNS = [
    r"app\.kubernetes\.io/name",
    r"app\.kubernetes\.io/instance",
    r"app\.kubernetes\.io/version",
    r"app\.kubernetes\.io/managed-by",
    r"helm\.sh/chart",
]
DEMO_CHART_YAML = """apiVersion: v2
name: demo-app
version: 0.1.0
"""

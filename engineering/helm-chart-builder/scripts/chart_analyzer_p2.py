# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402
# fmt: off
from chart_analyzer_p1 import CHART_YAML_CHECKS, REQUIRED_FILES  # noqa: E402,E501
# fmt: on


DEMO_VALUES_YAML = """replicaCount: 1

image:
  repository: nginx
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 80
"""
DEMO_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: demo-app
          image: nginx:1.25
          ports:
            - containerPort: 80
"""
def parse_yaml_simple(content):
    """Simple key-value parser for YAML (stdlib only)."""
    result = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip("'\"")
            if val:
                result[key] = val
    return result
def check_structure(chart_dir):
    """Check chart directory for required files."""
    findings = []
    for check in REQUIRED_FILES:
        path = chart_dir / check["path"]
        if not path.exists():
            findings.append({
                "id": "ST" + str(REQUIRED_FILES.index(check) + 1).zfill(3),
                "severity": check["severity"],
                "message": check["message"],
                "fix": f"Create {check['path']}",
                "file": check["path"],
            })
    return findings
def check_chart_yaml(chart_dir):
    """Validate Chart.yaml metadata."""
    findings = []
    chart_path = chart_dir / "Chart.yaml"
    if not chart_path.exists():
        return findings

    content = chart_path.read_text(encoding="utf-8")
    parsed = parse_yaml_simple(content)

    for check in CHART_YAML_CHECKS:
        if check["field"] not in parsed:
            findings.append({
                "id": "CY" + str(CHART_YAML_CHECKS.index(check) + 1).zfill(3),
                "severity": check["severity"],
                "message": check["message"],
                "fix": f"Add '{check['field']}:' to Chart.yaml",
                "file": "Chart.yaml",
            })

    # Check apiVersion value
    if parsed.get("apiVersion") == "v1":
        findings.append({
            "id": "CY007",
            "severity": "medium",
            "message": "apiVersion: v1 is Helm 2 format — use v2 for Helm 3",
            "fix": "Change apiVersion to v2",
            "file": "Chart.yaml",
        })

    # Check version is semver
    version = parsed.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+", version):
        findings.append({
            "id": "CY008",
            "severity": "high",
            "message": f"Version '{version}' is not valid semver",
            "fix": "Use semver format: MAJOR.MINOR.PATCH (e.g., 1.0.0)",
            "file": "Chart.yaml",
        })

    return findings

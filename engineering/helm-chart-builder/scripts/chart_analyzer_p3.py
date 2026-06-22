# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402
# fmt: off
from chart_analyzer_p1 import LABEL_PATTERNS, TEMPLATE_ANTI_PATTERNS  # noqa: E402,E501
# fmt: on


def check_templates(chart_dir):
    """Scan templates for anti-patterns."""
    findings = []
    templates_dir = chart_dir / "templates"
    if not templates_dir.exists():
        return findings

    template_files = list(templates_dir.glob("*.yaml")) + list(templates_dir.glob("*.yml")) + list(templates_dir.glob("*.tpl"))

    all_content = ""
    for tpl_file in template_files:
        content = tpl_file.read_text(encoding="utf-8")
        all_content += content + "\n"
        rel_path = tpl_file.relative_to(chart_dir)

        for rule in TEMPLATE_ANTI_PATTERNS:
            # Skip patterns that would false-positive on template expressions
            for match in re.finditer(rule["pattern"], content, re.MULTILINE):
                line = match.group(0).strip()
                # Skip if the line contains a template expression
                if "{{" in line or "}}" in line:
                    continue
                findings.append({
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "file": str(rel_path),
                    "line": line[:80],
                })

    # Check for standard labels
    helpers_file = templates_dir / "_helpers.tpl"
    if helpers_file.exists():
        helpers_content = helpers_file.read_text(encoding="utf-8")
        for label_pattern in LABEL_PATTERNS:
            if not re.search(label_pattern, helpers_content) and not re.search(label_pattern, all_content):
                label_name = label_pattern.replace("\\.", ".")
                findings.append({
                    "id": "LB001",
                    "severity": "high",
                    "message": f"Standard label '{label_name}' not found in helpers or templates",
                    "fix": f"Add {label_name} to the labels helper in _helpers.tpl",
                    "file": "templates/_helpers.tpl",
                    "line": "(label not found)",
                })

    # Check for resource limits
    if "resources:" not in all_content and template_files:
        findings.append({
            "id": "TP006",
            "severity": "critical",
            "message": "No resource requests/limits in any template — pods can consume unlimited node resources",
            "fix": "Add resources section: {{ toYaml .Values.resources | nindent 12 }}",
            "file": "templates/",
            "line": "(no resources block found)",
        })

    # Check for probes
    if "livenessProbe" not in all_content and "readinessProbe" not in all_content and template_files:
        has_deployment = any("Deployment" in f.read_text(encoding="utf-8") for f in template_files if f.suffix in (".yaml", ".yml"))
        if has_deployment:
            findings.append({
                "id": "TP007",
                "severity": "high",
                "message": "No liveness/readiness probes — Kubernetes cannot detect unhealthy pods",
                "fix": "Add livenessProbe and readinessProbe with configurable values",
                "file": "templates/deployment.yaml",
                "line": "(no probes found)",
            })

    return findings

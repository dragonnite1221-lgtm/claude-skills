# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from values_validator_base import *  # noqa: F403,E402
# fmt: off
from values_validator_p1 import SECRET_KEY_PATTERNS  # noqa: E402,E501
# fmt: on


def validate_documentation(entries):
    """Check documentation coverage."""
    findings = []
    total = len(entries)
    documented = sum(1 for e in entries if e["has_documentation"])

    if total > 0:
        coverage = (documented / total) * 100
        if coverage < 50:
            findings.append({
                "severity": "high",
                "category": "documentation",
                "message": f"Only {coverage:.0f}% of values have comments ({documented}/{total})",
                "fix": "Add inline YAML comments explaining purpose, type, and valid options for each value",
                "line": 0,
            })
        elif coverage < 80:
            findings.append({
                "severity": "medium",
                "category": "documentation",
                "message": f"{coverage:.0f}% documentation coverage ({documented}/{total}) — aim for 80%+",
                "fix": "Add comments for undocumented values",
                "line": 0,
            })

    # Flag specific undocumented top-level keys
    for entry in entries:
        if entry["depth"] == 1 and not entry["has_documentation"]:
            findings.append({
                "severity": "low",
                "category": "documentation",
                "message": f"Top-level key '{entry['key']}' has no comment",
                "fix": f"Add a comment above '{entry['key']}' explaining its purpose",
                "line": entry["line"],
            })

    return findings
def validate_defaults(entries):
    """Check default value quality."""
    findings = []

    for entry in entries:
        # Check for :latest tag
        if entry["key"] == "tag" and entry["value"] in ("latest", '"latest"', "'latest'"):
            findings.append({
                "severity": "high",
                "category": "defaults",
                "message": f"image.tag defaults to 'latest' — not reproducible",
                "fix": "Use a specific version tag or reference .Chart.AppVersion in template",
                "line": entry["line"],
            })

        # Check pullPolicy
        if entry["key"] == "pullPolicy" and entry["value"] in ("Always", '"Always"', "'Always'"):
            findings.append({
                "severity": "low",
                "category": "defaults",
                "message": "imagePullPolicy defaults to 'Always' — 'IfNotPresent' is better for production",
                "fix": "Change default to IfNotPresent (Always is appropriate for :latest only)",
                "line": entry["line"],
            })

        # Check empty resources
        if entry["key"] == "resources" and entry["value_type"] == "empty_map":
            findings.append({
                "severity": "medium",
                "category": "defaults",
                "message": "resources defaults to {} — no requests or limits set",
                "fix": "Provide default resource requests (e.g., cpu: 100m, memory: 128Mi)",
                "line": entry["line"],
            })

    return findings
def validate_secrets(entries):
    """Check for secrets in default values."""
    findings = []

    for entry in entries:
        for pattern in SECRET_KEY_PATTERNS:
            if pattern.search(entry["full_path"]):
                val = entry["value"].strip("'\"")
                if val and val not in ("", "null", "~", "{}", "[]", "changeme", "CHANGEME", "TODO", '""', "''"):
                    findings.append({
                        "severity": "critical",
                        "category": "security",
                        "message": f"Potential secret with default value: {entry['full_path']} = {val[:30]}...",
                        "fix": "Remove default. Use empty string, null, or 'changeme' placeholder with comment",
                        "line": entry["line"],
                    })
                break

    return findings
def validate_depth(entries):
    """Check nesting depth."""
    findings = []
    max_depth = max((e["depth"] for e in entries), default=0)

    if max_depth > 4:
        deep_entries = [e for e in entries if e["depth"] > 4]
        for entry in deep_entries[:3]:  # Report first 3
            findings.append({
                "severity": "medium",
                "category": "structure",
                "message": f"Deeply nested key ({entry['depth']} levels): {entry['full_path']}",
                "fix": "Flatten structure — max 3-4 levels deep for usability",
                "line": entry["line"],
            })

    return findings

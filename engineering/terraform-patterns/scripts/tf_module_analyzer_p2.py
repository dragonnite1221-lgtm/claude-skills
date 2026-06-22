# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_module_analyzer_base import *  # noqa: F403,E402
# fmt: off
from tf_module_analyzer_p1 import EXPECTED_FILES, VALID_RESOURCE_NAME  # noqa: E402,E501
# fmt: on


def parse_variables(content):
    """Extract variable declarations with metadata."""
    variables = []
    # Match variable blocks
    for match in re.finditer(
        r'^variable\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.MULTILINE | re.DOTALL,
    ):
        name = match.group(1)
        body = match.group(2)
        var = {
            "name": name,
            "has_description": "description" in body,
            "has_type": bool(re.search(r'\btype\s*=', body)),
            "has_default": bool(re.search(r'\bdefault\s*=', body)),
            "has_validation": "validation" in body,
            "is_sensitive": "sensitive" in body and bool(
                re.search(r'\bsensitive\s*=\s*true', body)
            ),
        }
        variables.append(var)
    return variables
def parse_outputs(content):
    """Extract output declarations with metadata."""
    outputs = []
    for match in re.finditer(
        r'^output\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.MULTILINE | re.DOTALL,
    ):
        name = match.group(1)
        body = match.group(2)
        out = {
            "name": name,
            "has_description": "description" in body,
            "is_sensitive": "sensitive" in body and bool(
                re.search(r'\bsensitive\s*=\s*true', body)
            ),
        }
        outputs.append(out)
    return outputs
def parse_modules(content):
    """Extract module calls."""
    modules = []
    for match in re.finditer(
        r'^module\s+"([^"]+)"\s*\{(.*?)\n\}',
        content,
        re.MULTILINE | re.DOTALL,
    ):
        name = match.group(1)
        body = match.group(2)
        source_match = re.search(r'source\s*=\s*"([^"]+)"', body)
        source = source_match.group(1) if source_match else "unknown"
        modules.append({"name": name, "source": source})
    return modules
def check_naming(resources, data_sources):
    """Check naming conventions."""
    issues = []
    for r in resources:
        if not VALID_RESOURCE_NAME.match(r["name"]):
            issues.append({
                "severity": "medium",
                "message": f"Resource '{r['type']}.{r['name']}' uses non-standard naming — use lowercase with underscores",
            })
        if r["name"].startswith(r["provider"] + "_"):
            issues.append({
                "severity": "low",
                "message": f"Resource '{r['type']}.{r['name']}' name repeats the provider prefix — redundant",
            })
    for d in data_sources:
        if not VALID_RESOURCE_NAME.match(d["name"]):
            issues.append({
                "severity": "medium",
                "message": f"Data source '{d['type']}.{d['name']}' uses non-standard naming",
            })
    return issues
def check_variables(variables):
    """Check variable quality."""
    issues = []
    for v in variables:
        if not v["has_description"]:
            issues.append({
                "severity": "medium",
                "message": f"Variable '{v['name']}' missing description — consumers won't know what to provide",
            })
        if not v["has_type"]:
            issues.append({
                "severity": "high",
                "message": f"Variable '{v['name']}' missing type constraint — accepts any value",
            })
        # Check if name suggests a secret
        secret_patterns = ["password", "secret", "token", "key", "api_key", "credentials"]
        name_lower = v["name"].lower()
        if any(p in name_lower for p in secret_patterns) and not v["is_sensitive"]:
            issues.append({
                "severity": "high",
                "message": f"Variable '{v['name']}' looks like a secret but is not marked sensitive = true",
            })
    return issues
def check_outputs(outputs):
    """Check output quality."""
    issues = []
    for o in outputs:
        if not o["has_description"]:
            issues.append({
                "severity": "low",
                "message": f"Output '{o['name']}' missing description",
            })
    return issues
def check_file_structure(tf_files):
    """Check if expected files are present."""
    issues = []
    filenames = set(tf_files.keys())
    for expected, purpose in EXPECTED_FILES.items():
        if expected not in filenames:
            issues.append({
                "severity": "medium" if expected != "versions.tf" else "high",
                "message": f"Missing '{expected}' — {purpose}",
            })
    return issues

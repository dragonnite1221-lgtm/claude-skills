# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402
# fmt: off
from code_quality_analyzer_p1 import KNOWN_VULNERABLE_DEPS, SECURITY_PATTERNS  # noqa: E402,E501
# fmt: on


def calculate_complexity(content: str, language: str) -> Dict:
    """Calculate cyclomatic complexity estimate."""
    # Count decision points
    decision_patterns = [
        r"\bif\b", r"\belse\b", r"\belif\b", r"\bfor\b", r"\bwhile\b",
        r"\bcase\b", r"\bcatch\b", r"\b\?\b", r"\b&&\b", r"\b\|\|\b",
        r"\band\b", r"\bor\b"
    ]

    complexity = 1  # Base complexity
    for pattern in decision_patterns:
        complexity += len(re.findall(pattern, content, re.IGNORECASE))

    # Count nesting depth
    max_depth = 0
    current_depth = 0
    for char in content:
        if char == "{":
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == "}":
            current_depth = max(0, current_depth - 1)

    return {
        "cyclomatic": complexity,
        "max_nesting": max_depth,
        "rating": "low" if complexity < 10 else "medium" if complexity < 20 else "high"
    }
def analyze_security(filepath: Path, content: str) -> List[Dict]:
    """Scan for security issues."""
    issues = []
    lines = content.split("\n")

    for pattern_name, pattern_info in SECURITY_PATTERNS.items():
        regex = re.compile(pattern_info["pattern"], re.IGNORECASE)
        for line_num, line in enumerate(lines, 1):
            if regex.search(line):
                issues.append({
                    "file": str(filepath),
                    "line": line_num,
                    "type": pattern_name,
                    "severity": pattern_info["severity"],
                    "message": pattern_info["message"]
                })

    return issues
def analyze_dependencies(project_path: Path) -> Dict:
    """Analyze project dependencies for issues."""
    findings = {
        "package_managers": [],
        "total_deps": 0,
        "outdated": [],
        "vulnerable": [],
        "recommendations": []
    }

    # Check package.json
    package_json = project_path / "package.json"
    if package_json.exists():
        findings["package_managers"].append("npm")
        try:
            with open(package_json) as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            findings["total_deps"] += len(deps)

            for dep, version in deps.items():
                # Check against known vulnerabilities
                if dep in KNOWN_VULNERABLE_DEPS:
                    vuln = KNOWN_VULNERABLE_DEPS[dep]
                    # Simplified version check
                    clean_version = re.sub(r"[^\d.]", "", version)
                    if clean_version and clean_version < vuln["vulnerable_below"]:
                        findings["vulnerable"].append({
                            "package": dep,
                            "current": version,
                            "fix_version": vuln["vulnerable_below"],
                            "cve": vuln["cve"]
                        })
        except Exception:
            pass

    # Check requirements.txt
    requirements = project_path / "requirements.txt"
    if requirements.exists():
        findings["package_managers"].append("pip")
        try:
            with open(requirements) as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            findings["total_deps"] += len(lines)
        except Exception:
            pass

    # Check go.mod
    go_mod = project_path / "go.mod"
    if go_mod.exists():
        findings["package_managers"].append("go")

    return findings

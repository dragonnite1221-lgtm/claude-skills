# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402


def generate_recommendations(analysis: Dict) -> List[Dict]:
    """Generate prioritized recommendations."""
    recs = []

    # Critical security issues
    for issue in analysis["security"]["critical"][:3]:
        recs.append({
            "priority": "P0",
            "category": "security",
            "issue": issue["message"],
            "file": issue["file"],
            "action": f"Remove or secure sensitive data at line {issue['line']}"
        })

    # Vulnerable dependencies
    for vuln in analysis["dependencies"].get("vulnerable", [])[:3]:
        recs.append({
            "priority": "P0",
            "category": "security",
            "issue": f"Vulnerable dependency: {vuln['package']} ({vuln['cve']})",
            "action": f"Update to version {vuln['fix_version']} or later"
        })

    # High security issues
    for issue in analysis["security"]["high"][:3]:
        recs.append({
            "priority": "P1",
            "category": "security",
            "issue": issue["message"],
            "file": issue["file"],
            "action": "Review and fix security vulnerability"
        })

    # Test coverage
    tests = analysis.get("tests", {})
    if tests.get("estimated_coverage", 0) < 50:
        recs.append({
            "priority": "P1",
            "category": "quality",
            "issue": f"Low test coverage: {tests.get('estimated_coverage', 0)}%",
            "action": "Add unit tests to improve coverage to at least 70%"
        })

    # High complexity files
    for cplx in analysis["complexity"]["high_complexity_files"][:2]:
        recs.append({
            "priority": "P2",
            "category": "maintainability",
            "issue": f"High complexity in {cplx['file']}",
            "action": "Refactor to reduce cyclomatic complexity"
        })

    # Documentation
    docs = analysis.get("documentation", {})
    if not docs.get("has_readme"):
        recs.append({
            "priority": "P2",
            "category": "documentation",
            "issue": "Missing README.md",
            "action": "Add README with project overview and setup instructions"
        })

    return recs[:10]

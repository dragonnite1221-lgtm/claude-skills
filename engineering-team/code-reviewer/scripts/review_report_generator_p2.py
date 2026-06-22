# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_report_generator_base import *  # noqa: F403,E402
# fmt: off
from review_report_generator_p1 import SEVERITY_WEIGHTS  # noqa: E402,E501
# fmt: on


def generate_findings_list(pr_analysis: Dict, quality_analysis: Dict) -> List[Dict]:
    """Combine and prioritize all findings."""
    findings = []

    # Add PR risk findings
    if "risks" in pr_analysis:
        for severity, items in pr_analysis["risks"].items():
            for item in items:
                findings.append({
                    "source": "pr_analysis",
                    "severity": severity,
                    "category": item.get("name", "unknown"),
                    "message": item.get("message", ""),
                    "file": item.get("file", ""),
                    "count": item.get("count", 1)
                })

    # Add code quality findings
    if "issues" in quality_analysis:
        for issue in quality_analysis["issues"]:
            findings.append({
                "source": "quality_analysis",
                "severity": issue.get("severity", "medium"),
                "category": issue.get("type", "unknown"),
                "message": issue.get("message", ""),
                "file": issue.get("file", ""),
                "line": issue.get("line", 0)
            })

    # Sort by severity weight
    findings.sort(
        key=lambda x: -SEVERITY_WEIGHTS.get(x["severity"], 0)
    )

    return findings
def get_action_for_category(category: str, finding: Dict) -> str:
    """Get actionable recommendation for issue category."""
    actions = {
        "hardcoded_secrets": "Remove hardcoded credentials and use environment variables or a secrets manager",
        "sql_concatenation": "Use parameterized queries to prevent SQL injection",
        "debugger": "Remove debugger statements before merging",
        "console_log": "Remove or replace console statements with proper logging",
        "todo_fixme": "Address TODO/FIXME comments or create tracking issues",
        "disable_eslint": "Address the underlying issue instead of disabling lint rules",
        "any_type": "Replace 'any' types with proper type definitions",
        "long_function": "Break down function into smaller, focused units",
        "god_class": "Split class into smaller, single-responsibility classes",
        "too_many_params": "Use parameter objects or builder pattern",
        "deep_nesting": "Refactor using early returns, guard clauses, or extraction",
        "high_complexity": "Reduce cyclomatic complexity through refactoring",
        "missing_error_handling": "Add proper error handling and recovery logic",
        "duplicate_code": "Extract duplicate code into shared functions",
        "magic_numbers": "Replace magic numbers with named constants",
        "large_file": "Consider splitting into multiple smaller modules"
    }
    return actions.get(category, f"Review and address: {finding.get('message', category)}")
def generate_action_items(findings: List[Dict]) -> List[Dict]:
    """Generate prioritized action items from findings."""
    action_items = []
    seen_categories = set()

    for finding in findings:
        category = finding["category"]
        severity = finding["severity"]

        # Group similar issues
        if category in seen_categories and severity not in ["critical", "high"]:
            continue

        action = {
            "priority": "P0" if severity == "critical" else "P1" if severity == "high" else "P2",
            "action": get_action_for_category(category, finding),
            "severity": severity,
            "files_affected": [finding["file"]] if finding.get("file") else []
        }
        action_items.append(action)
        seen_categories.add(category)

    return action_items[:15]  # Top 15 actions

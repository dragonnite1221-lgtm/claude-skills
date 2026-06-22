# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gdpr_compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from gdpr_compliance_checker_p1 import SKIP_PATTERNS  # noqa: E402,E501
# fmt: on


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(skip in path.parts for skip in SKIP_PATTERNS)
def scan_file_for_patterns(
    filepath: Path,
    patterns: Dict
) -> List[Dict]:
    """Scan a file for pattern matches."""
    findings = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

        for pattern_name, pattern_info in patterns.items():
            regex = re.compile(pattern_info["pattern"], re.IGNORECASE)

            for line_num, line in enumerate(lines, 1):
                matches = regex.findall(line)
                if matches:
                    findings.append({
                        "file": str(filepath),
                        "line": line_num,
                        "pattern": pattern_name,
                        "matches": len(matches) if isinstance(matches, list) else 1,
                        **{k: v for k, v in pattern_info.items() if k != "pattern"}
                    })

    except Exception as e:
        pass  # Skip files that can't be read

    return findings
def generate_recommendations(
    personal_data: List[Dict],
    code_issues: List[Dict],
    config_issues: List[Dict]
) -> List[Dict]:
    """Generate prioritized recommendations."""
    recommendations = []
    seen_issues = set()

    # Critical issues first
    for finding in code_issues:
        if finding.get("severity") == "critical":
            issue_key = finding.get("issue", "")
            if issue_key not in seen_issues:
                recommendations.append({
                    "priority": "P0",
                    "issue": finding.get("issue"),
                    "gdpr_article": finding.get("gdpr_article"),
                    "action": finding.get("recommendation"),
                    "affected_files": [finding.get("file")]
                })
                seen_issues.add(issue_key)

    # Special category data
    special_category_files = set()
    for finding in personal_data:
        if finding.get("category") == "special_category":
            special_category_files.add(finding.get("file"))

    if special_category_files:
        recommendations.append({
            "priority": "P0",
            "issue": "Special category personal data (Art. 9) detected",
            "gdpr_article": "Art. 9(1)",
            "action": "Ensure explicit consent or other Art. 9(2) legal basis exists",
            "affected_files": list(special_category_files)[:5]
        })

    # High priority issues
    for finding in code_issues:
        if finding.get("severity") == "high":
            issue_key = finding.get("issue", "")
            if issue_key not in seen_issues:
                recommendations.append({
                    "priority": "P1",
                    "issue": finding.get("issue"),
                    "gdpr_article": finding.get("gdpr_article"),
                    "action": finding.get("recommendation"),
                    "affected_files": [finding.get("file")]
                })
                seen_issues.add(issue_key)

    # Config issues
    for finding in config_issues:
        recommendations.append({
            "priority": "P1",
            "issue": finding.get("issue"),
            "gdpr_article": finding.get("gdpr_article"),
            "action": f"Update configuration in {finding.get('file')}",
            "affected_files": [finding.get("file")]
        })

    return recommendations[:15]

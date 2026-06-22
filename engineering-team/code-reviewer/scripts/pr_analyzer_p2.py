# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pr_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pr_analyzer_p1 import FILE_CATEGORIES, RISK_PATTERNS, run_git_command  # noqa: E402,E501
# fmt: on


def get_changed_files(repo_path: Path, base: str, head: str) -> List[Dict]:
    """Get list of changed files between two refs."""
    success, output = run_git_command(
        ["git", "diff", "--name-status", f"{base}...{head}"],
        repo_path
    )

    if not success:
        # Try without the triple dot (for uncommitted changes)
        success, output = run_git_command(
            ["git", "diff", "--name-status", base, head],
            repo_path
        )

    if not success or not output:
        # Fall back to staged changes
        success, output = run_git_command(
            ["git", "diff", "--name-status", "--cached"],
            repo_path
        )

    files = []
    for line in output.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0][0]  # First character of status
            filepath = parts[-1]  # Handle renames (R100\told\tnew)
            status_map = {
                "A": "added",
                "M": "modified",
                "D": "deleted",
                "R": "renamed",
                "C": "copied"
            }
            files.append({
                "path": filepath,
                "status": status_map.get(status, "modified")
            })

    return files
def get_file_diff(repo_path: Path, filepath: str, base: str, head: str) -> str:
    """Get diff content for a specific file."""
    success, output = run_git_command(
        ["git", "diff", f"{base}...{head}", "--", filepath],
        repo_path
    )
    if not success:
        success, output = run_git_command(
            ["git", "diff", "--cached", "--", filepath],
            repo_path
        )
    return output if success else ""
def categorize_file(filepath: str) -> Tuple[str, int]:
    """Categorize a file based on its path and name."""
    filepath_lower = filepath.lower()

    for category, info in FILE_CATEGORIES.items():
        for pattern in info["patterns"]:
            if re.search(pattern, filepath_lower):
                return category, info["weight"]

    return "medium", 2  # Default category
def analyze_diff_for_risks(diff_content: str, filepath: str) -> List[Dict]:
    """Analyze diff content for risky patterns."""
    risks = []

    # Only analyze added lines (starting with +)
    added_lines = [
        line[1:] for line in diff_content.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]

    content = "\n".join(added_lines)

    for risk in RISK_PATTERNS:
        matches = re.findall(risk["pattern"], content, re.IGNORECASE)
        if matches:
            risks.append({
                "name": risk["name"],
                "severity": risk["severity"],
                "message": risk["message"],
                "file": filepath,
                "count": len(matches)
            })

    return risks
def count_changes(diff_content: str) -> Dict[str, int]:
    """Count additions and deletions in diff."""
    additions = 0
    deletions = 0

    for line in diff_content.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

    return {"additions": additions, "deletions": deletions}
def calculate_complexity_score(files: List[Dict], all_risks: List[Dict]) -> int:
    """Calculate overall PR complexity score (1-10)."""
    score = 0

    # File count contribution (max 3 points)
    file_count = len(files)
    if file_count > 20:
        score += 3
    elif file_count > 10:
        score += 2
    elif file_count > 5:
        score += 1

    # Total changes contribution (max 3 points)
    total_changes = sum(f.get("additions", 0) + f.get("deletions", 0) for f in files)
    if total_changes > 500:
        score += 3
    elif total_changes > 200:
        score += 2
    elif total_changes > 50:
        score += 1

    # Risk severity contribution (max 4 points)
    critical_risks = sum(1 for r in all_risks if r["severity"] == "critical")
    high_risks = sum(1 for r in all_risks if r["severity"] == "high")

    score += min(2, critical_risks)
    score += min(2, high_risks)

    return min(10, max(1, score))

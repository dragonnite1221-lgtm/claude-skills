# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pr_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pr_analyzer_p1 import run_git_command  # noqa: E402,E501
from pr_analyzer_p2 import analyze_diff_for_risks, calculate_complexity_score, categorize_file, count_changes, get_changed_files, get_file_diff  # noqa: E402,E501
# fmt: on


def analyze_commit_messages(repo_path: Path, base: str, head: str) -> Dict:
    """Analyze commit messages in the PR."""
    success, output = run_git_command(
        ["git", "log", "--oneline", f"{base}...{head}"],
        repo_path
    )

    if not success or not output:
        return {"commits": 0, "issues": []}

    commits = output.strip().split("\n")
    issues = []

    for commit in commits:
        if len(commit) < 10:
            continue

        # Check for conventional commit format
        message = commit[8:] if len(commit) > 8 else commit  # Skip hash

        if not re.match(r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?:", message):
            issues.append({
                "commit": commit[:7],
                "issue": "Does not follow conventional commit format"
            })

        if len(message) > 72:
            issues.append({
                "commit": commit[:7],
                "issue": "Commit message exceeds 72 characters"
            })

    return {
        "commits": len(commits),
        "issues": issues
    }
def get_complexity_label(score: int) -> str:
    """Get human-readable complexity label."""
    if score <= 2:
        return "Simple"
    elif score <= 4:
        return "Moderate"
    elif score <= 6:
        return "Complex"
    elif score <= 8:
        return "Very Complex"
    else:
        return "Critical"
def analyze_pr(
    repo_path: Path,
    base: str = "main",
    head: str = "HEAD"
) -> Dict:
    """Perform complete PR analysis."""
    # Get changed files
    changed_files = get_changed_files(repo_path, base, head)

    if not changed_files:
        return {
            "status": "no_changes",
            "message": "No changes detected between branches"
        }

    # Analyze each file
    all_risks = []
    file_analyses = []

    for file_info in changed_files:
        filepath = file_info["path"]
        category, weight = categorize_file(filepath)

        # Get diff for the file
        diff = get_file_diff(repo_path, filepath, base, head)
        changes = count_changes(diff)
        risks = analyze_diff_for_risks(diff, filepath)

        all_risks.extend(risks)

        file_analyses.append({
            "path": filepath,
            "status": file_info["status"],
            "category": category,
            "priority_weight": weight,
            "additions": changes["additions"],
            "deletions": changes["deletions"],
            "risks": risks
        })

    # Sort by priority (highest first)
    file_analyses.sort(key=lambda x: (-x["priority_weight"], x["path"]))

    # Analyze commits
    commit_analysis = analyze_commit_messages(repo_path, base, head)

    # Calculate metrics
    complexity = calculate_complexity_score(file_analyses, all_risks)

    total_additions = sum(f["additions"] for f in file_analyses)
    total_deletions = sum(f["deletions"] for f in file_analyses)

    return {
        "status": "analyzed",
        "summary": {
            "files_changed": len(file_analyses),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "complexity_score": complexity,
            "complexity_label": get_complexity_label(complexity),
            "commits": commit_analysis["commits"]
        },
        "risks": {
            "critical": [r for r in all_risks if r["severity"] == "critical"],
            "high": [r for r in all_risks if r["severity"] == "high"],
            "medium": [r for r in all_risks if r["severity"] == "medium"],
            "low": [r for r in all_risks if r["severity"] == "low"]
        },
        "files": file_analyses,
        "commit_issues": commit_analysis["issues"],
        "review_order": [f["path"] for f in file_analyses[:10]]  # Top 10 priority files
    }

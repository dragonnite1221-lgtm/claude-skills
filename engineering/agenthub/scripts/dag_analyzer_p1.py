# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dag_analyzer_base import *  # noqa: F403,E402


def run_git(*args):
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr.strip()}", file=sys.stderr)
        return ""
def get_hub_branches(session_id=None):
    """Get all hub/* branches, optionally filtered by session."""
    output = run_git("branch", "--list", "hub/*", "--format=%(refname:short)")
    if not output:
        return []
    branches = output.strip().split("\n")
    if session_id:
        prefix = f"hub/{session_id}/"
        branches = [b for b in branches if b.startswith(prefix)]
    return branches
def get_branch_commit(branch):
    """Get the commit hash for a branch."""
    return run_git("rev-parse", "--short", branch)
def get_branch_commit_count(branch, base_branch="main"):
    """Count commits ahead of base branch."""
    output = run_git("rev-list", "--count", f"{base_branch}..{branch}")
    try:
        return int(output)
    except ValueError:
        return 0
def get_branch_last_commit_date(branch):
    """Get the last commit date for a branch."""
    output = run_git("log", "-1", "--format=%ci", branch)
    if output:
        return output[:19]
    return "unknown"
def get_branch_last_commit_msg(branch):
    """Get the last commit message for a branch."""
    return run_git("log", "-1", "--format=%s", branch)
def detect_frontier(session_id=None):
    """Find frontier branches (tips with no child branches).

    A branch is on the frontier if no other hub branch contains its tip commit
    as an ancestor (i.e., it has no children in the DAG).
    """
    branches = get_hub_branches(session_id)
    if not branches:
        return []

    # Get commit hashes for all branches
    branch_commits = {}
    for b in branches:
        commit = run_git("rev-parse", b)
        if commit:
            branch_commits[b] = commit

    # A branch is frontier if its commit is not an ancestor of any other branch
    frontier = []
    for branch, commit in branch_commits.items():
        is_ancestor = False
        for other_branch, other_commit in branch_commits.items():
            if other_branch == branch:
                continue
            # Check if commit is ancestor of other_commit
            result = subprocess.run(
                ["git", "merge-base", "--is-ancestor", commit, other_commit],
                capture_output=True
            )
            if result.returncode == 0:
                is_ancestor = True
                break
        if not is_ancestor:
            frontier.append(branch)

    return frontier
def show_graph():
    """Display the git DAG graph for hub branches."""
    branches = get_hub_branches()
    if not branches:
        print("No hub/* branches found.")
        return

    # Use git log with graph for hub branches
    branch_args = [b for b in branches]
    output = run_git(
        "log", "--all", "--oneline", "--graph", "--decorate",
        "--simplify-by-decoration",
        *[f"--branches=hub/*"]
    )
    if output:
        print(output)
    else:
        print("No hub commits found.")

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dag_analyzer_base import *  # noqa: F403,E402
# fmt: off
from dag_analyzer_p1 import detect_frontier, get_branch_commit, get_branch_commit_count, get_branch_last_commit_date, get_branch_last_commit_msg, get_hub_branches  # noqa: E402,E501
# fmt: on


def show_status(session_id, output_format="table"):
    """Show per-agent branch status for a session."""
    branches = get_hub_branches(session_id)
    if not branches:
        print(f"No branches found for session {session_id}")
        return

    frontier = detect_frontier(session_id)

    # Parse agent info from branch names
    agents = []
    for branch in sorted(branches):
        # Pattern: hub/{session}/agent-{N}/attempt-{M}
        match = re.match(r"hub/[^/]+/agent-(\d+)/attempt-(\d+)", branch)
        if match:
            agent_num = int(match.group(1))
            attempt = int(match.group(2))
        else:
            agent_num = 0
            attempt = 1

        commit = get_branch_commit(branch)
        commits = get_branch_commit_count(branch)
        last_date = get_branch_last_commit_date(branch)
        last_msg = get_branch_last_commit_msg(branch)
        is_frontier = branch in frontier

        agents.append({
            "agent": agent_num,
            "attempt": attempt,
            "branch": branch,
            "commit": commit,
            "commits_ahead": commits,
            "last_update": last_date,
            "last_message": last_msg,
            "frontier": is_frontier,
        })

    if output_format == "json":
        print(json.dumps({"session": session_id, "agents": agents}, indent=2))
        return

    # Table output
    print(f"Session: {session_id}")
    print(f"Branches: {len(branches)} | Frontier: {len(frontier)}")
    print()
    header = f"{'AGENT':<8} {'BRANCH':<45} {'COMMITS':<8} {'STATUS':<10} {'LAST UPDATE':<20}"
    print(header)
    print("-" * len(header))
    for a in agents:
        status = "frontier" if a["frontier"] else "merged"
        print(f"agent-{a['agent']:<4} {a['branch']:<45} {a['commits_ahead']:<8} {status:<10} {a['last_update']:<20}")
def run_demo():
    """Show demo output."""
    print("=" * 60)
    print("AgentHub DAG Analyzer — Demo Mode")
    print("=" * 60)
    print()

    print("--- Frontier Detection ---")
    print("Frontier branches (leaves with no children):")
    print("  hub/20260317-143022/agent-1/attempt-1  (3 commits ahead)")
    print("  hub/20260317-143022/agent-2/attempt-1  (5 commits ahead)")
    print("  hub/20260317-143022/agent-3/attempt-1  (2 commits ahead)")
    print()

    print("--- Session Status ---")
    print("Session: 20260317-143022")
    print("Branches: 3 | Frontier: 3")
    print()
    header = f"{'AGENT':<8} {'BRANCH':<45} {'COMMITS':<8} {'STATUS':<10} {'LAST UPDATE':<20}"
    print(header)
    print("-" * len(header))
    print(f"{'agent-1':<8} {'hub/20260317-143022/agent-1/attempt-1':<45} {'3':<8} {'frontier':<10} {'2026-03-17 14:35:10':<20}")
    print(f"{'agent-2':<8} {'hub/20260317-143022/agent-2/attempt-1':<45} {'5':<8} {'frontier':<10} {'2026-03-17 14:36:45':<20}")
    print(f"{'agent-3':<8} {'hub/20260317-143022/agent-3/attempt-1':<45} {'2':<8} {'frontier':<10} {'2026-03-17 14:34:22':<20}")
    print()

    print("--- DAG Graph ---")
    print("* abc1234 (hub/20260317-143022/agent-2/attempt-1) Replaced O(n²) with hash map")
    print("* def5678 Added benchmark tests")
    print("| * ghi9012 (hub/20260317-143022/agent-1/attempt-1) Added caching layer")
    print("| * jkl3456 Refactored data access")
    print("|/")
    print("| * mno7890 (hub/20260317-143022/agent-3/attempt-1) Minor optimizations")
    print("|/")
    print("* pqr1234 (dev) Base commit")

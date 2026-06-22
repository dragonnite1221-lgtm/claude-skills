# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from session_manager_base import *  # noqa: F403,E402
# fmt: off
from session_manager_p1 import VALID_STATES, VALID_TRANSITIONS, load_config, load_state, run_git, save_state  # noqa: E402,E501
# fmt: on


def update_state(session_id, new_state):
    """Transition session to a new state."""
    state = load_state(session_id)
    if not state:
        print(f"Error: Session {session_id} not found", file=sys.stderr)
        sys.exit(1)

    current = state.get("state", "unknown")

    if new_state not in VALID_STATES:
        print(f"Error: Invalid state '{new_state}'. "
              f"Valid: {', '.join(VALID_STATES)}", file=sys.stderr)
        sys.exit(1)

    valid_next = VALID_TRANSITIONS.get(current, [])
    if new_state not in valid_next:
        print(f"Error: Cannot transition from '{current}' to '{new_state}'. "
              f"Valid transitions: {', '.join(valid_next) or 'none (terminal)'}",
              file=sys.stderr)
        sys.exit(1)

    state["state"] = new_state
    save_state(session_id, state)
    print(f"Session {session_id}: {current} → {new_state}")
def cleanup_session(session_id):
    """Clean up worktrees and optionally archive branches."""
    config = load_config(session_id)
    if not config:
        print(f"Error: Session {session_id} not found", file=sys.stderr)
        sys.exit(1)

    # Find and remove worktrees for this session
    worktree_output = run_git("worktree", "list", "--porcelain")
    removed = 0
    if worktree_output:
        current_path = None
        for line in worktree_output.split("\n"):
            if line.startswith("worktree "):
                current_path = line[len("worktree "):]
            elif line.startswith("branch ") and current_path:
                ref = line[len("branch "):]
                if f"hub/{session_id}/" in ref:
                    result = subprocess.run(
                        ["git", "worktree", "remove", "--force", current_path],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        removed += 1
                        print(f"  Removed worktree: {current_path}")
                current_path = None

    print(f"Cleaned up {removed} worktrees for session {session_id}")
def run_demo():
    """Show demo output."""
    print("=" * 60)
    print("AgentHub Session Manager — Demo Mode")
    print("=" * 60)
    print()

    print("--- Session List ---")
    print("AgentHub Sessions")
    print()
    header = f"{'SESSION ID':<20} {'STATE':<12} {'AGENTS':<8} {'TASK'}"
    print(header)
    print("-" * 70)
    print(f"{'20260317-143022':<20} {'merged':<12} {'3':<8} Optimize API response time below 100ms")
    print(f"{'20260317-151500':<20} {'running':<12} {'2':<8} Refactor auth module for JWT support")
    print(f"{'20260317-160000':<20} {'init':<12} {'4':<8} Implement caching strategy")
    print()

    print("--- Session Detail ---")
    print("Session: 20260317-143022")
    print("  State: merged")
    print("  Task: Optimize API response time below 100ms")
    print("  Agents: 3")
    print("  Base branch: dev")
    print("  Eval: pytest bench.py --json")
    print("  Metric: p50_ms (lower)")
    print("  Created: 2026-03-17T14:30:22Z")
    print("  Updated: 2026-03-17T14:45:00Z")
    print()
    print("  Branches:")
    print("    hub/20260317-143022/agent-1/attempt-1  (archived)")
    print("    hub/20260317-143022/agent-2/attempt-1  (merged)")
    print("    hub/20260317-143022/agent-3/attempt-1  (archived)")
    print()

    print("--- State Transitions ---")
    print("Valid transitions:")
    for state, transitions in VALID_TRANSITIONS.items():
        arrow = " → ".join(transitions) if transitions else "(terminal)"
        print(f"  {state}: {arrow}")

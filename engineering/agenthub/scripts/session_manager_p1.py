# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from session_manager_base import *  # noqa: F403,E402


SESSIONS_PATH = ".agenthub/sessions"
VALID_STATES = ["init", "running", "evaluating", "merged", "archived"]
VALID_TRANSITIONS = {
    "init": ["running"],
    "running": ["evaluating"],
    "evaluating": ["merged", "archived"],
    "merged": [],
    "archived": [],
}
def load_state(session_id):
    """Load session state.json."""
    state_path = os.path.join(SESSIONS_PATH, session_id, "state.json")
    if not os.path.exists(state_path):
        return None
    with open(state_path) as f:
        return json.load(f)
def save_state(session_id, state):
    """Save session state.json."""
    state_path = os.path.join(SESSIONS_PATH, session_id, "state.json")
    state["updated"] = datetime.now(timezone.utc).isoformat()
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
def load_config(session_id):
    """Load session config.yaml (simple key: value parsing)."""
    config_path = os.path.join(SESSIONS_PATH, session_id, "config.yaml")
    if not os.path.exists(config_path):
        return None
    config = {}
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                config[key.strip()] = val.strip().strip('"')
    return config
def run_git(*args):
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""
def list_sessions(output_format="text"):
    """List all sessions with their states."""
    if not os.path.isdir(SESSIONS_PATH):
        print("No sessions found. Run hub_init.py first.")
        return

    sessions = []
    for sid in sorted(os.listdir(SESSIONS_PATH)):
        session_dir = os.path.join(SESSIONS_PATH, sid)
        if not os.path.isdir(session_dir):
            continue
        state = load_state(sid)
        config = load_config(sid)
        if state and config:
            sessions.append({
                "session_id": sid,
                "state": state.get("state", "unknown"),
                "task": config.get("task", ""),
                "agents": config.get("agent_count", "?"),
                "created": state.get("created", ""),
            })

    if output_format == "json":
        print(json.dumps({"sessions": sessions}, indent=2))
        return

    if not sessions:
        print("No sessions found.")
        return

    print("AgentHub Sessions")
    print()
    header = f"{'SESSION ID':<20} {'STATE':<12} {'AGENTS':<8} {'TASK'}"
    print(header)
    print("-" * 70)
    for s in sessions:
        task = s["task"][:40] + "..." if len(s["task"]) > 40 else s["task"]
        print(f"{s['session_id']:<20} {s['state']:<12} {s['agents']:<8} {task}")
def show_status(session_id, output_format="text"):
    """Show detailed status for a session."""
    state = load_state(session_id)
    config = load_config(session_id)

    if not state or not config:
        print(f"Error: Session {session_id} not found", file=sys.stderr)
        sys.exit(1)

    if output_format == "json":
        print(json.dumps({"config": config, "state": state}, indent=2))
        return

    print(f"Session: {session_id}")
    print(f"  State: {state.get('state', 'unknown')}")
    print(f"  Task: {config.get('task', '')}")
    print(f"  Agents: {config.get('agent_count', '?')}")
    print(f"  Base branch: {config.get('base_branch', '?')}")
    if config.get("eval_cmd"):
        print(f"  Eval: {config['eval_cmd']}")
    if config.get("metric"):
        print(f"  Metric: {config['metric']} ({config.get('direction', '?')})")
    print(f"  Created: {state.get('created', '?')}")
    print(f"  Updated: {state.get('updated', '?')}")

    # Show agent branches
    branches = run_git("branch", "--list", f"hub/{session_id}/*",
                       "--format=%(refname:short)")
    if branches:
        print()
        print("  Branches:")
        for b in branches.split("\n"):
            if b.strip():
                print(f"    {b.strip()}")

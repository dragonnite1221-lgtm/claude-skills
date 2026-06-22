# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hub_init_base import *  # noqa: F403,E402


def generate_session_id():
    """Generate a timestamp-based session ID."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")
def create_directory_structure(base_path):
    """Create the .agenthub/ directory tree."""
    dirs = [
        os.path.join(base_path, "sessions"),
        os.path.join(base_path, "board", "dispatch"),
        os.path.join(base_path, "board", "progress"),
        os.path.join(base_path, "board", "results"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
def write_gitignore(base_path):
    """Write .agenthub/.gitignore to exclude worktree artifacts."""
    gitignore_path = os.path.join(base_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("# AgentHub gitignore\n")
            f.write("# Keep board and sessions, ignore worktree artifacts\n")
            f.write("*.tmp\n")
            f.write("*.lock\n")
def write_board_index(base_path):
    """Initialize the board index file."""
    index_path = os.path.join(base_path, "board", "_index.json")
    if not os.path.exists(index_path):
        index = {
            "channels": ["dispatch", "progress", "results"],
            "counters": {"dispatch": 0, "progress": 0, "results": 0},
        }
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
            f.write("\n")
def create_session(base_path, session_id, task, agents, eval_cmd, metric,
                   direction, base_branch):
    """Create a new session with config and state files."""
    session_dir = os.path.join(base_path, "sessions", session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Write config.yaml (manual YAML to avoid dependency)
    config_path = os.path.join(session_dir, "config.yaml")
    config_lines = [
        f"session_id: {session_id}",
        f"task: \"{task}\"",
        f"agent_count: {agents}",
        f"base_branch: {base_branch}",
        f"created: {datetime.now(timezone.utc).isoformat()}",
    ]
    if eval_cmd:
        config_lines.append(f"eval_cmd: \"{eval_cmd}\"")
    if metric:
        config_lines.append(f"metric: {metric}")
    if direction:
        config_lines.append(f"direction: {direction}")

    with open(config_path, "w") as f:
        f.write("\n".join(config_lines))
        f.write("\n")

    # Write state.json
    state_path = os.path.join(session_dir, "state.json")
    state = {
        "session_id": session_id,
        "state": "init",
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "agents": {},
    }
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    return session_dir
def validate_git_repo():
    """Check if current directory is a git repository."""
    if not os.path.isdir(".git"):
        # Check parent dirs
        path = os.path.abspath(".")
        while path != "/":
            if os.path.isdir(os.path.join(path, ".git")):
                return True
            path = os.path.dirname(path)
        return False
    return True
def get_current_branch():
    """Get the current git branch name."""
    head_file = os.path.join(".git", "HEAD")
    if os.path.exists(head_file):
        with open(head_file) as f:
            ref = f.read().strip()
            if ref.startswith("ref: refs/heads/"):
                return ref[len("ref: refs/heads/"):]
    return "main"

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from result_ranker_base import *  # noqa: F403,E402


def run_git(*args):
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""
def get_session_config(session_id):
    """Load session config."""
    config_path = os.path.join(".agenthub", "sessions", session_id, "config.yaml")
    if not os.path.exists(config_path):
        print(f"Error: Session {session_id} not found", file=sys.stderr)
        sys.exit(1)

    config = {}
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                val = val.strip().strip('"')
                config[key.strip()] = val
    return config
def get_hub_branches(session_id):
    """Get all hub branches for a session."""
    output = run_git("branch", "--list", f"hub/{session_id}/*",
                     "--format=%(refname:short)")
    if not output:
        return []
    return [b.strip() for b in output.split("\n") if b.strip()]
def get_worktree_path(branch):
    """Get the worktree path for a branch, if it exists."""
    output = run_git("worktree", "list", "--porcelain")
    if not output:
        return None
    current_path = None
    for line in output.split("\n"):
        if line.startswith("worktree "):
            current_path = line[len("worktree "):]
        elif line.startswith("branch ") and current_path:
            ref = line[len("branch "):]
            short = ref.replace("refs/heads/", "")
            if short == branch:
                return current_path
            current_path = None
    return None
def run_eval_in_worktree(worktree_path, eval_cmd):
    """Run evaluation command in a worktree and return stdout."""
    try:
        result = subprocess.run(
            eval_cmd, shell=True, capture_output=True, text=True,
            cwd=worktree_path, timeout=120
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1
    except Exception as e:
        return str(e), 1
def extract_metric(output, metric_name):
    """Extract a numeric metric from command output.

    Looks for patterns like:
    - metric_name: 42.5
    - metric_name=42.5
    - "metric_name": 42.5
    """
    patterns = [
        rf'{metric_name}\s*[:=]\s*([\d.]+)',
        rf'"{metric_name}"\s*[:=]\s*([\d.]+)',
        rf"'{metric_name}'\s*[:=]\s*([\d.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None
def get_diff_stats(branch, base_branch="main"):
    """Get diff statistics for a branch vs base."""
    output = run_git("diff", "--stat", f"{base_branch}...{branch}")
    lines_output = run_git("diff", "--shortstat", f"{base_branch}...{branch}")

    files_changed = 0
    insertions = 0
    deletions = 0

    if lines_output:
        files_match = re.search(r"(\d+) files? changed", lines_output)
        ins_match = re.search(r"(\d+) insertions?", lines_output)
        del_match = re.search(r"(\d+) deletions?", lines_output)
        if files_match:
            files_changed = int(files_match.group(1))
        if ins_match:
            insertions = int(ins_match.group(1))
        if del_match:
            deletions = int(del_match.group(1))

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "net_lines": insertions - deletions,
    }
def rank_by_metric(results, direction="lower"):
    """Sort results by metric value."""
    valid = [r for r in results if r.get("metric_value") is not None]
    invalid = [r for r in results if r.get("metric_value") is None]

    reverse = direction == "higher"
    valid.sort(key=lambda r: r["metric_value"], reverse=reverse)

    for i, r in enumerate(valid):
        r["rank"] = i + 1

    for r in invalid:
        r["rank"] = len(valid) + 1

    return valid + invalid

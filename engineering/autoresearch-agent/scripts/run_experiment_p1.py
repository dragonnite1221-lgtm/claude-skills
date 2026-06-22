# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from run_experiment_base import *  # noqa: F403,E402


def find_autoresearch_root():
    """Find .autoresearch/ in project or user home."""
    project_root = Path(".").resolve() / ".autoresearch"
    if project_root.exists():
        return project_root
    user_root = Path.home() / ".autoresearch"
    if user_root.exists():
        return user_root
    return None
def load_config(experiment_dir):
    """Load config.cfg from experiment directory."""
    cfg_file = experiment_dir / "config.cfg"
    if not cfg_file.exists():
        print(f"  Error: no config.cfg in {experiment_dir}")
        sys.exit(1)
    config = {}
    for line in cfg_file.read_text().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            config[k.strip()] = v.strip()
    return config
def run_git(args, cwd=None, timeout=30):
    """Run a git command safely (no shell injection). Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True,
        cwd=cwd, timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()
def get_current_commit(path):
    """Get short hash of current HEAD."""
    _, commit, _ = run_git(["rev-parse", "--short", "HEAD"], cwd=path)
    return commit
def get_best_metric(experiment_dir, direction):
    """Read the best metric from results.tsv."""
    tsv = experiment_dir / "results.tsv"
    if not tsv.exists():
        return None
    lines = [l for l in tsv.read_text().splitlines()[1:] if "\tkeep\t" in l]
    if not lines:
        return None
    metrics = []
    for line in lines:
        parts = line.split("\t")
        try:
            if parts[1] != "N/A":
                metrics.append(float(parts[1]))
        except (ValueError, IndexError):
            continue
    if not metrics:
        return None
    return min(metrics) if direction == "lower" else max(metrics)
def run_evaluation(project_root, eval_cmd, time_budget_minutes, log_file):
    """Run evaluation with time limit. Output goes to log_file.

    Note: shell=True is intentional here — eval_cmd is user-provided and
    may contain pipes, redirects, or chained commands.
    """
    hard_limit = time_budget_minutes * 60 * 2.5
    t0 = time.time()
    try:
        with open(log_file, "w") as lf:
            result = subprocess.run(
                eval_cmd, shell=True,
                stdout=lf, stderr=subprocess.STDOUT,
                cwd=str(project_root),
                timeout=hard_limit
            )
        elapsed = time.time() - t0
        return result.returncode, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return -1, elapsed
def extract_metric(log_file, metric_grep):
    """Extract metric value from log file."""
    log_path = Path(log_file)
    if not log_path.exists():
        return None
    for line in reversed(log_path.read_text().splitlines()):
        stripped = line.strip()
        if stripped.startswith(metric_grep.lstrip("^")):
            try:
                return float(stripped.split(":")[-1].strip())
            except ValueError:
                continue
    return None
def is_improvement(new_val, old_val, direction):
    """Check if new result is better than old."""
    if old_val is None:
        return True
    if direction == "lower":
        return new_val < old_val
    return new_val > old_val
def log_result(experiment_dir, commit, metric_val, status, description):
    """Append result to results.tsv."""
    tsv = experiment_dir / "results.tsv"
    metric_str = f"{metric_val:.6f}" if metric_val is not None else "N/A"
    with open(tsv, "a") as f:
        f.write(f"{commit}\t{metric_str}\t{status}\t{description}\n")
def get_experiment_count(experiment_dir):
    """Count experiments run so far."""
    tsv = experiment_dir / "results.tsv"
    if not tsv.exists():
        return 0
    return max(0, len(tsv.read_text().splitlines()) - 1)
def get_description_from_diff(project_root):
    """Auto-generate a description from git diff --stat HEAD~1."""
    code, diff_stat, _ = run_git(["diff", "--stat", "HEAD~1"], cwd=str(project_root))
    if code == 0 and diff_stat:
        return diff_stat.split("\n")[0][:50]
    return "experiment"
def read_last_lines(filepath, n=5):
    """Read last n lines of a file (replaces tail shell command)."""
    path = Path(filepath)
    if not path.exists():
        return ""
    lines = path.read_text().splitlines()
    return "\n".join(lines[-n:])

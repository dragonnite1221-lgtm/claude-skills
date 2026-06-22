# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from run_experiment_base import *  # noqa: F403,E402
# fmt: off
from run_experiment_p1 import extract_metric, find_autoresearch_root, get_best_metric, get_current_commit, get_description_from_diff, get_experiment_count, is_improvement, load_config, log_result, read_last_lines, run_evaluation, run_git  # noqa: E402,E501
# fmt: on


def run_single(project_root, experiment_dir, config, exp_num, dry_run=False, description=None):
    """Run one experiment iteration."""
    direction = config.get("metric_direction", "lower")
    metric_grep = config.get("metric_grep", "^metric:")
    eval_cmd = config.get("evaluate_cmd", "python evaluate.py")
    time_budget = int(config.get("time_budget_minutes", 5))
    metric_name = config.get("metric", "metric")
    log_file = str(experiment_dir / "run.log")

    best = get_best_metric(experiment_dir, direction)
    ts = datetime.now().strftime("%H:%M:%S")

    print(f"\n[{ts}] Experiment #{exp_num}")
    print(f"  Best {metric_name}: {best}")

    if dry_run:
        print("  [DRY RUN] Would run evaluation and check metric")
        return "dry_run"

    # Auto-generate description if not provided
    if not description:
        description = get_description_from_diff(str(project_root))

    # Run evaluation
    print(f"  Running: {eval_cmd} (budget: {time_budget}m)")
    ret_code, elapsed = run_evaluation(project_root, eval_cmd, time_budget, log_file)

    commit = get_current_commit(str(project_root))

    # Timeout
    if ret_code == -1:
        print(f"  TIMEOUT after {elapsed:.0f}s — discarding")
        run_git(["checkout", "--", "."], cwd=str(project_root))
        run_git(["reset", "--hard", "HEAD~1"], cwd=str(project_root))
        log_result(experiment_dir, commit, None, "crash", f"timeout_{elapsed:.0f}s")
        return "crash"

    # Crash
    if ret_code != 0:
        tail = read_last_lines(log_file, 5)
        print(f"  CRASH (exit {ret_code}) after {elapsed:.0f}s")
        print(f"  Last output: {tail[:200]}")
        run_git(["reset", "--hard", "HEAD~1"], cwd=str(project_root))
        log_result(experiment_dir, commit, None, "crash", f"exit_{ret_code}")
        return "crash"

    # Extract metric
    metric_val = extract_metric(log_file, metric_grep)
    if metric_val is None:
        print(f"  Could not parse {metric_name} from run.log")
        run_git(["reset", "--hard", "HEAD~1"], cwd=str(project_root))
        log_result(experiment_dir, commit, None, "crash", "metric_parse_failed")
        return "crash"

    delta = ""
    if best is not None:
        diff = metric_val - best
        delta = f" (delta {diff:+.4f})"

    print(f"  {metric_name}: {metric_val:.6f}{delta} in {elapsed:.0f}s")

    # Keep or discard
    if is_improvement(metric_val, best, direction):
        print(f"  KEEP — improvement")
        log_result(experiment_dir, commit, metric_val, "keep", description)
        return "keep"
    else:
        print(f"  DISCARD — no improvement")
        run_git(["reset", "--hard", "HEAD~1"], cwd=str(project_root))
        best_str = f"{best:.4f}" if best is not None else "?"
        log_result(experiment_dir, commit, metric_val, "discard",
                   f"no_improvement_{metric_val:.4f}_vs_{best_str}")
        return "discard"
def main():
    parser = argparse.ArgumentParser(description="autoresearch-agent runner")
    parser.add_argument("--experiment", help="Experiment path: domain/name (e.g. engineering/api-speed)")
    parser.add_argument("--single", action="store_true", help="Run one experiment iteration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--description", help="Description of the change (auto-generated from git diff if omitted)")
    parser.add_argument("--path", default=".", help="Project root")
    args = parser.parse_args()

    project_root = Path(args.path).resolve()
    root = find_autoresearch_root()

    if root is None:
        print("No .autoresearch/ found. Run setup_experiment.py first.")
        sys.exit(1)

    if not args.experiment:
        print("Specify --experiment domain/name")
        sys.exit(1)

    experiment_dir = root / args.experiment
    if not experiment_dir.exists():
        print(f"Experiment not found: {experiment_dir}")
        print("Run: python scripts/setup_experiment.py --list")
        sys.exit(1)

    config = load_config(experiment_dir)

    print(f"\n  autoresearch-agent")
    print(f"  Experiment: {args.experiment}")
    print(f"  Target: {config.get('target', '?')}")
    print(f"  Metric: {config.get('metric', '?')} ({config.get('metric_direction', '?')} is better)")
    print(f"  Budget: {config.get('time_budget_minutes', '?')} min/experiment")
    print(f"  Mode: {'dry-run' if args.dry_run else 'single'}")

    exp_num = get_experiment_count(experiment_dir) + 1
    run_single(project_root, experiment_dir, config, exp_num, args.dry_run, args.description)

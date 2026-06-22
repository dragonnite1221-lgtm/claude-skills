# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from log_results_base import *  # noqa: F403,E402


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
    """Load config.cfg."""
    cfg_file = experiment_dir / "config.cfg"
    config = {}
    if cfg_file.exists():
        for line in cfg_file.read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                config[k.strip()] = v.strip()
    return config
def load_results(experiment_dir):
    """Load results.tsv into list of dicts."""
    tsv = experiment_dir / "results.tsv"
    if not tsv.exists():
        return []
    results = []
    for line in tsv.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 4:
            try:
                metric = float(parts[1]) if parts[1] != "N/A" else None
            except ValueError:
                metric = None
            results.append({
                "commit": parts[0],
                "metric": metric,
                "status": parts[2],
                "description": parts[3],
            })
    return results
def compute_stats(results, direction):
    """Compute statistics from results."""
    keeps = [r for r in results if r["status"] == "keep"]
    discards = [r for r in results if r["status"] == "discard"]
    crashes = [r for r in results if r["status"] == "crash"]

    valid_keeps = [r for r in keeps if r["metric"] is not None]
    baseline = valid_keeps[0]["metric"] if valid_keeps else None
    if valid_keeps:
        best = min(r["metric"] for r in valid_keeps) if direction == "lower" else max(r["metric"] for r in valid_keeps)
    else:
        best = None

    pct_change = None
    if baseline is not None and best is not None and baseline != 0:
        if direction == "lower":
            pct_change = (baseline - best) / baseline * 100
        else:
            pct_change = (best - baseline) / baseline * 100

    return {
        "total": len(results),
        "keeps": len(keeps),
        "discards": len(discards),
        "crashes": len(crashes),
        "baseline": baseline,
        "best": best,
        "pct_change": pct_change,
    }
def print_experiment(experiment_dir, experiment_path):
    """Print single experiment results to terminal."""
    config = load_config(experiment_dir)
    results = load_results(experiment_dir)
    direction = config.get("metric_direction", "lower")
    metric_name = config.get("metric", "metric")

    if not results:
        print(f"No results for {experiment_path}")
        return

    stats = compute_stats(results, direction)

    print(f"\n{'─' * 65}")
    print(f"  {experiment_path}")
    print(f"  Target: {config.get('target', '?')} | Metric: {metric_name} ({direction})")
    print(f"{'─' * 65}")
    print(f"  Total: {stats['total']} | Keep: {stats['keeps']} | Discard: {stats['discards']} | Crash: {stats['crashes']}")

    if stats["baseline"] is not None and stats["best"] is not None:
        pct = f" ({stats['pct_change']:+.1f}%)" if stats["pct_change"] is not None else ""
        print(f"  Baseline: {stats['baseline']:.6f} -> Best: {stats['best']:.6f}{pct}")

    print(f"\n  {'COMMIT':<10} {'METRIC':>12} {'STATUS':<10} DESCRIPTION")
    print(f"  {'─' * 60}")
    for r in results:
        m = f"{r['metric']:.6f}" if r["metric"] is not None else "N/A     "
        icon = {"keep": "+", "discard": "-", "crash": "!"}.get(r["status"], "?")
        print(f"  {r['commit']:<10} {m:>12} {icon} {r['status']:<7} {r['description'][:35]}")
    print()

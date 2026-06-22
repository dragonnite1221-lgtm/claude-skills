# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from log_results_base import *  # noqa: F403,E402
# fmt: off
from log_results_p1 import compute_stats, load_config, load_results  # noqa: E402,E501
# fmt: on


def print_dashboard(root):
    """Print cross-experiment dashboard."""
    experiments = []
    for domain_dir in sorted(root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("."):
            continue
        for exp_dir in sorted(domain_dir.iterdir()):
            if not exp_dir.is_dir() or not (exp_dir / "config.cfg").exists():
                continue
            config = load_config(exp_dir)
            results = load_results(exp_dir)
            direction = config.get("metric_direction", "lower")
            stats = compute_stats(results, direction)

            best_str = f"{stats['best']:.4f}" if stats["best"] is not None else "—"
            pct_str = f"{stats['pct_change']:+.1f}%" if stats["pct_change"] is not None else "—"

            # Determine status
            status = "idle"
            if stats["total"] > 0:
                tsv = exp_dir / "results.tsv"
                if tsv.exists():
                    age_hours = (time.time() - tsv.stat().st_mtime) / 3600
                    status = "active" if age_hours < 1 else "paused" if age_hours < 24 else "done"

            experiments.append({
                "domain": domain_dir.name,
                "name": exp_dir.name,
                "runs": stats["total"],
                "kept": stats["keeps"],
                "best": best_str,
                "change": pct_str,
                "status": status,
                "metric": config.get("metric", "?"),
            })

    if not experiments:
        print("No experiments found.")
        return experiments

    print(f"\n{'─' * 90}")
    print(f"  autoresearch — Dashboard")
    print(f"{'─' * 90}")
    print(f"  {'DOMAIN':<15} {'EXPERIMENT':<20} {'RUNS':>5} {'KEPT':>5} {'BEST':>12} {'CHANGE':>10} {'STATUS':<8}")
    print(f"  {'─' * 85}")
    for e in experiments:
        print(f"  {e['domain']:<15} {e['name']:<20} {e['runs']:>5} {e['kept']:>5} {e['best']:>12} {e['change']:>10} {e['status']:<8}")
    print()
    return experiments
def export_experiment_csv(experiment_dir, experiment_path):
    """Export single experiment as CSV string."""
    config = load_config(experiment_dir)
    results = load_results(experiment_dir)
    direction = config.get("metric_direction", "lower")
    stats = compute_stats(results, direction)

    buf = io.StringIO()
    writer = csv.writer(buf)

    # Header with metadata
    writer.writerow(["# Experiment", experiment_path])
    writer.writerow(["# Target", config.get("target", "")])
    writer.writerow(["# Metric", f"{config.get('metric', '')} ({direction} is better)"])
    if stats["baseline"] is not None:
        writer.writerow(["# Baseline", f"{stats['baseline']:.6f}"])
    if stats["best"] is not None:
        pct = f" ({stats['pct_change']:+.1f}%)" if stats["pct_change"] is not None else ""
        writer.writerow(["# Best", f"{stats['best']:.6f}{pct}"])
    writer.writerow(["# Total", stats["total"]])
    writer.writerow(["# Keep/Discard/Crash", f"{stats['keeps']}/{stats['discards']}/{stats['crashes']}"])
    writer.writerow([])

    writer.writerow(["Commit", "Metric", "Status", "Description"])
    for r in results:
        m = f"{r['metric']:.6f}" if r["metric"] is not None else "N/A"
        writer.writerow([r["commit"], m, r["status"], r["description"]])

    return buf.getvalue()
def export_dashboard_csv(root, domain_filter=None):
    """Export dashboard as CSV string."""
    experiments = []
    for domain_dir in sorted(root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("."):
            continue
        if domain_filter and domain_dir.name != domain_filter:
            continue
        for exp_dir in sorted(domain_dir.iterdir()):
            if not exp_dir.is_dir() or not (exp_dir / "config.cfg").exists():
                continue
            config = load_config(exp_dir)
            results = load_results(exp_dir)
            direction = config.get("metric_direction", "lower")
            stats = compute_stats(results, direction)
            best_str = f"{stats['best']:.6f}" if stats["best"] is not None else ""
            pct_str = f"{stats['pct_change']:+.1f}%" if stats["pct_change"] is not None else ""
            experiments.append([
                domain_dir.name, exp_dir.name, config.get("metric", ""),
                stats["total"], stats["keeps"], stats["discards"], stats["crashes"],
                best_str, pct_str
            ])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Domain", "Experiment", "Metric", "Runs", "Kept", "Discarded", "Crashed", "Best", "Change"])
    for e in experiments:
        writer.writerow(e)
    return buf.getvalue()

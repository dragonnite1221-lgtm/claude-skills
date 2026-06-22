# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from log_results_base import *  # noqa: F403,E402
# fmt: off
from log_results_p1 import compute_stats, load_config, load_results  # noqa: E402,E501
# fmt: on


def export_experiment_markdown(experiment_dir, experiment_path):
    """Export single experiment as Markdown string."""
    config = load_config(experiment_dir)
    results = load_results(experiment_dir)
    direction = config.get("metric_direction", "lower")
    metric_name = config.get("metric", "metric")
    stats = compute_stats(results, direction)

    lines = []
    lines.append(f"# Autoresearch: {experiment_path}\n")
    lines.append(f"**Target:** `{config.get('target', '?')}`  ")
    lines.append(f"**Metric:** `{metric_name}` ({direction} is better)  ")
    lines.append(f"**Experiments:** {stats['total']} total — {stats['keeps']} kept, {stats['discards']} discarded, {stats['crashes']} crashed\n")

    if stats["baseline"] is not None and stats["best"] is not None:
        pct = f" ({stats['pct_change']:+.1f}%)" if stats["pct_change"] is not None else ""
        lines.append(f"**Progress:** `{stats['baseline']:.6f}` → `{stats['best']:.6f}`{pct}\n")

    lines.append(f"| Commit | Metric | Status | Description |")
    lines.append(f"|--------|--------|--------|-------------|")
    for r in results:
        m = f"`{r['metric']:.6f}`" if r["metric"] is not None else "N/A"
        lines.append(f"| `{r['commit']}` | {m} | {r['status']} | {r['description']} |")
    lines.append("")

    return "\n".join(lines)
def export_dashboard_markdown(root, domain_filter=None):
    """Export dashboard as Markdown string."""
    lines = []
    lines.append("# Autoresearch Dashboard\n")
    lines.append("| Domain | Experiment | Metric | Runs | Kept | Best | Change | Status |")
    lines.append("|--------|-----------|--------|------|------|------|--------|--------|")

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
            best = f"`{stats['best']:.4f}`" if stats["best"] is not None else "—"
            pct = f"{stats['pct_change']:+.1f}%" if stats["pct_change"] is not None else "—"

            tsv = exp_dir / "results.tsv"
            status = "idle"
            if tsv.exists() and stats["total"] > 0:
                age_h = (time.time() - tsv.stat().st_mtime) / 3600
                status = "active" if age_h < 1 else "paused" if age_h < 24 else "done"

            lines.append(f"| {domain_dir.name} | {exp_dir.name} | {config.get('metric', '?')} | {stats['total']} | {stats['keeps']} | {best} | {pct} | {status} |")

    lines.append("")
    return "\n".join(lines)

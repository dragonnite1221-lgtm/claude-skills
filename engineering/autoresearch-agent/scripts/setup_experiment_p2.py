# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from setup_experiment_base import *  # noqa: F403,E402
# fmt: off
from setup_experiment_p1 import EVALUATOR_DIR  # noqa: E402,E501
# fmt: on


def list_experiments(root):
    """List all experiments across all domains."""
    if not root.exists():
        print("No experiments found. Run setup to create your first experiment.")
        return

    experiments = []
    for domain_dir in sorted(root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("."):
            continue
        for exp_dir in sorted(domain_dir.iterdir()):
            if not exp_dir.is_dir():
                continue
            cfg_file = exp_dir / "config.cfg"
            if not cfg_file.exists():
                continue
            config = {}
            for line in cfg_file.read_text().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    config[k.strip()] = v.strip()

            # Count results
            tsv = exp_dir / "results.tsv"
            runs = 0
            if tsv.exists():
                runs = max(0, len(tsv.read_text().splitlines()) - 1)

            experiments.append({
                "domain": domain_dir.name,
                "name": exp_dir.name,
                "target": config.get("target", "?"),
                "metric": config.get("metric", "?"),
                "runs": runs,
            })

    if not experiments:
        print("No experiments found.")
        return

    print(f"\n{'DOMAIN':<15} {'EXPERIMENT':<25} {'TARGET':<30} {'METRIC':<15} {'RUNS':>5}")
    print("-" * 95)
    for e in experiments:
        print(f"{e['domain']:<15} {e['name']:<25} {e['target']:<30} {e['metric']:<15} {e['runs']:>5}")
    print(f"\nTotal: {len(experiments)} experiments")
def list_evaluators():
    """List available built-in evaluators."""
    if not EVALUATOR_DIR.exists():
        print("No evaluators directory found.")
        return

    print(f"\nAvailable evaluators ({EVALUATOR_DIR}):\n")
    for f in sorted(EVALUATOR_DIR.glob("*.py")):
        # Read first docstring line
        desc = ""
        for line in f.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                # Single-line docstring: """Description."""
                after_quote = stripped[3:]
                if after_quote and after_quote.rstrip(quote[0]).strip():
                    desc = after_quote.rstrip('"').rstrip("'").strip()
                    break
                continue
            if stripped and not line.startswith("#!"):
                desc = stripped.strip('"').strip("'")
                break
        print(f"  {f.stem:<25} {desc}")

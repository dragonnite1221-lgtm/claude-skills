# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from log_results_base import *  # noqa: F403,E402
# fmt: off
from log_results_p1 import find_autoresearch_root, print_experiment  # noqa: E402,E501
from log_results_p2 import export_dashboard_csv, export_experiment_csv, print_dashboard  # noqa: E402,E501
from log_results_p3 import export_dashboard_markdown, export_experiment_markdown  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(description="autoresearch-agent results viewer")
    parser.add_argument("--experiment", help="Show one experiment: domain/name")
    parser.add_argument("--domain", help="Show all experiments in a domain")
    parser.add_argument("--dashboard", action="store_true", help="Cross-experiment dashboard")
    parser.add_argument("--format", choices=["terminal", "csv", "markdown"], default="terminal",
                        help="Output format (default: terminal)")
    parser.add_argument("--output", "-o", help="Write to file instead of stdout")
    parser.add_argument("--all", action="store_true", help="Show all experiments (alias for --dashboard)")
    args = parser.parse_args()

    root = find_autoresearch_root()
    if root is None:
        print("No .autoresearch/ found. Run setup_experiment.py first.")
        sys.exit(1)

    output_text = None

    # Single experiment
    if args.experiment:
        experiment_dir = root / args.experiment
        if not experiment_dir.exists():
            print(f"Experiment not found: {args.experiment}")
            sys.exit(1)

        if args.format == "csv":
            output_text = export_experiment_csv(experiment_dir, args.experiment)
        elif args.format == "markdown":
            output_text = export_experiment_markdown(experiment_dir, args.experiment)
        else:
            print_experiment(experiment_dir, args.experiment)
            return

    # Domain
    elif args.domain:
        domain_dir = root / args.domain
        if not domain_dir.exists():
            print(f"Domain not found: {args.domain}")
            sys.exit(1)
        for exp_dir in sorted(domain_dir.iterdir()):
            if exp_dir.is_dir() and (exp_dir / "config.cfg").exists():
                if args.format == "terminal":
                    print_experiment(exp_dir, f"{args.domain}/{exp_dir.name}")
                # For CSV/MD, fall through to dashboard with domain filter
        if args.format != "terminal":
            # Use dashboard export filtered to domain
            output_text = export_dashboard_csv(root, domain_filter=args.domain) if args.format == "csv" else export_dashboard_markdown(root, domain_filter=args.domain)
        else:
            return

    # Dashboard
    elif args.dashboard or args.all:
        if args.format == "csv":
            output_text = export_dashboard_csv(root)
        elif args.format == "markdown":
            output_text = export_dashboard_markdown(root)
        else:
            print_dashboard(root)
            return

    else:
        # Default: dashboard
        if args.format == "terminal":
            print_dashboard(root)
            return
        output_text = export_dashboard_csv(root) if args.format == "csv" else export_dashboard_markdown(root)

    # Write output
    if output_text:
        if args.output:
            Path(args.output).write_text(output_text)
            print(f"Written to {args.output}")
        else:
            print(output_text)

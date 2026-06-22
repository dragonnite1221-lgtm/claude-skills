# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from setup_experiment_base import *  # noqa: F403,E402
# fmt: off
from setup_experiment_p1 import DOMAINS, copy_evaluator, create_branch, create_config, create_program_md, get_autoresearch_root, init_results_tsv, init_root, run_cmd  # noqa: E402,E501
from setup_experiment_p2 import list_evaluators, list_experiments  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(description="autoresearch-agent setup")
    parser.add_argument("--domain", choices=DOMAINS, help="Experiment domain")
    parser.add_argument("--name", help="Experiment name (e.g. api-speed, medium-ctr)")
    parser.add_argument("--target", help="Target file to optimize")
    parser.add_argument("--eval", dest="eval_cmd", help="Evaluation command")
    parser.add_argument("--metric", help="Metric name (must appear in eval output as 'name: value')")
    parser.add_argument("--direction", choices=["lower", "higher"], default="lower",
                        help="Is lower or higher better?")
    parser.add_argument("--time-budget", type=int, default=5, help="Minutes per experiment (default: 5)")
    parser.add_argument("--evaluator", help="Built-in evaluator to copy (e.g. benchmark_speed)")
    parser.add_argument("--scope", choices=["project", "user"], default="project",
                        help="Where to store experiments: project (./) or user (~/)")
    parser.add_argument("--constraints", default="", help="Additional constraints for program.md")
    parser.add_argument("--path", default=".", help="Project root path")
    parser.add_argument("--skip-branch", action="store_true", help="Don't create git branch")
    parser.add_argument("--list", action="store_true", help="List all experiments")
    parser.add_argument("--list-evaluators", action="store_true", help="List available evaluators")
    args = parser.parse_args()

    project_root = Path(args.path).resolve()

    # List mode
    if args.list:
        root = get_autoresearch_root("project", project_root)
        list_experiments(root)
        user_root = get_autoresearch_root("user")
        if user_root.exists() and user_root != root:
            print(f"\n--- User-level experiments ({user_root}) ---")
            list_experiments(user_root)
        return

    if args.list_evaluators:
        list_evaluators()
        return

    # Validate required args for setup
    if not all([args.domain, args.name, args.target, args.eval_cmd, args.metric]):
        parser.error("Required: --domain, --name, --target, --eval, --metric")

    root = get_autoresearch_root(args.scope, project_root)

    print(f"\n  autoresearch-agent setup")
    print(f"  Project: {project_root}")
    print(f"  Scope: {args.scope}")
    print(f"  Domain: {args.domain}")
    print(f"  Experiment: {args.name}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Check git
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=str(project_root), capture_output=True, text=True
    )
    code = result.returncode
    if code != 0:
        print("  Error: not a git repository. Run: git init && git add . && git commit -m 'initial'")
        sys.exit(1)
    print("  Git repository found")

    # Check target file
    target_path = project_root / args.target
    if not target_path.exists():
        print(f"  Error: target file not found: {args.target}")
        sys.exit(1)
    print(f"  Target file found: {args.target}")

    # Init root
    init_root(root)

    # Create experiment directory
    experiment_dir = root / args.domain / args.name
    if experiment_dir.exists():
        print(f"  Warning: experiment '{args.domain}/{args.name}' already exists.")
        print(f"  Use --name with a different name, or delete {experiment_dir}")
        sys.exit(1)
    experiment_dir.mkdir(parents=True)
    print(f"  Created {experiment_dir}/")

    # Create files
    create_program_md(experiment_dir, args.domain, args.name,
                      args.target, args.metric, args.direction, args.constraints)
    print("  Created program.md")

    create_config(experiment_dir, args.target, args.eval_cmd,
                  args.metric, args.direction, args.time_budget)
    print("  Created config.cfg")

    init_results_tsv(experiment_dir)

    # Copy evaluator if specified
    if args.evaluator:
        copy_evaluator(experiment_dir, args.evaluator)

    # Create git branch
    if not args.skip_branch:
        create_branch(str(project_root), args.domain, args.name)

    # Test evaluation command
    print(f"\n  Testing evaluation: {args.eval_cmd}")
    code, out, err = run_cmd(args.eval_cmd, cwd=str(project_root), timeout=60)
    if code != 0:
        print(f"  Warning: eval command failed (exit {code})")
        if err:
            print(f"  stderr: {err[:200]}")
        print("  Fix the eval command before running the experiment loop.")
    else:
        # Check metric is parseable
        full_output = out + "\n" + err
        metric_found = False
        for line in full_output.splitlines():
            if line.strip().startswith(f"{args.metric}:"):
                metric_found = True
                print(f"  Eval works. Baseline: {line.strip()}")
                break
        if not metric_found:
            print(f"  Warning: eval ran but '{args.metric}:' not found in output.")
            print(f"  Make sure your eval command outputs: {args.metric}: <value>")

    # Summary
    print(f"\n  Setup complete!")
    print(f"  Experiment: {args.domain}/{args.name}")
    print(f"  Target: {args.target}")
    print(f"  Metric: {args.metric} ({args.direction} is better)")
    print(f"  Budget: {args.time_budget} min/experiment")
    if not args.skip_branch:
        print(f"  Branch: autoresearch/{args.domain}/{args.name}")
    print(f"\n  To start:")
    print(f"  python scripts/run_experiment.py --experiment {args.domain}/{args.name} --single")

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hub_init_base import *  # noqa: F403,E402
# fmt: off
from hub_init_p1 import create_directory_structure, create_session, generate_session_id, get_current_branch, validate_git_repo, write_board_index, write_gitignore  # noqa: E402,E501
# fmt: on


def run_demo():
    """Show a demo of what hub_init creates."""
    print("=" * 60)
    print("AgentHub Init — Demo Mode")
    print("=" * 60)
    print()
    print("Session ID: 20260317-143022")
    print("Task: Optimize API response time below 100ms")
    print("Agents: 3")
    print("Eval: pytest bench.py --json")
    print("Metric: p50_ms (lower is better)")
    print("Base branch: dev")
    print()
    print("Directory structure created:")
    print("  .agenthub/")
    print("  ├── .gitignore")
    print("  ├── sessions/")
    print("  │   └── 20260317-143022/")
    print("  │       ├── config.yaml")
    print("  │       └── state.json")
    print("  └── board/")
    print("      ├── _index.json")
    print("      ├── dispatch/")
    print("      ├── progress/")
    print("      └── results/")
    print()
    print("config.yaml:")
    print('  session_id: 20260317-143022')
    print('  task: "Optimize API response time below 100ms"')
    print("  agent_count: 3")
    print("  base_branch: dev")
    print('  eval_cmd: "pytest bench.py --json"')
    print("  metric: p50_ms")
    print("  direction: lower")
    print()
    print("state.json:")
    print('  { "state": "init", "agents": {} }')
    print()
    print("Next step: Run /hub:spawn to launch agents")
def main():
    parser = argparse.ArgumentParser(
        description="Initialize an AgentHub collaboration session"
    )
    parser.add_argument("--task", type=str, help="Task description for agents")
    parser.add_argument("--agents", type=int, default=3,
                        help="Number of parallel agents (default: 3)")
    parser.add_argument("--eval", type=str, dest="eval_cmd",
                        help="Evaluation command to run in each worktree")
    parser.add_argument("--metric", type=str,
                        help="Metric name to extract from eval output")
    parser.add_argument("--direction", choices=["lower", "higher"],
                        help="Whether lower or higher metric is better")
    parser.add_argument("--base-branch", type=str,
                        help="Base branch (default: current branch)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--demo", action="store_true",
                        help="Show demo output without creating files")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if not args.task:
        print("Error: --task is required", file=sys.stderr)
        print("Usage: hub_init.py --task 'description' [--agents N] "
              "[--eval 'cmd'] [--metric name] [--direction lower|higher]",
              file=sys.stderr)
        sys.exit(1)

    if not validate_git_repo():
        print("Error: Not a git repository. AgentHub requires git.",
              file=sys.stderr)
        sys.exit(1)

    base_branch = args.base_branch or get_current_branch()
    base_path = ".agenthub"
    session_id = generate_session_id()

    # Create structure
    create_directory_structure(base_path)
    write_gitignore(base_path)
    write_board_index(base_path)

    # Create session
    session_dir = create_session(
        base_path, session_id, args.task, args.agents,
        args.eval_cmd, args.metric, args.direction, base_branch
    )

    if args.format == "json":
        output = {
            "session_id": session_id,
            "session_dir": session_dir,
            "task": args.task,
            "agent_count": args.agents,
            "eval_cmd": args.eval_cmd,
            "metric": args.metric,
            "direction": args.direction,
            "base_branch": base_branch,
            "state": "init",
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"AgentHub session initialized")
        print(f"  Session ID: {session_id}")
        print(f"  Task: {args.task}")
        print(f"  Agents: {args.agents}")
        if args.eval_cmd:
            print(f"  Eval: {args.eval_cmd}")
        if args.metric:
            direction_str = "lower is better" if args.direction == "lower" else "higher is better"
            print(f"  Metric: {args.metric} ({direction_str})")
        print(f"  Base branch: {base_branch}")
        print(f"  State: init")
        print()
        print(f"Next step: Run /hub:spawn to launch {args.agents} agents")

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from result_ranker_base import *  # noqa: F403,E402
# fmt: off
from result_ranker_p1 import extract_metric, get_diff_stats, get_hub_branches, get_session_config, get_worktree_path, rank_by_metric, run_eval_in_worktree  # noqa: E402,E501
from result_ranker_p2 import run_demo  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Rank AgentHub agent results"
    )
    parser.add_argument("--session", type=str,
                        help="Session ID to evaluate")
    parser.add_argument("--eval-cmd", type=str,
                        help="Evaluation command to run in each worktree")
    parser.add_argument("--metric", type=str,
                        help="Metric name to extract from eval output")
    parser.add_argument("--direction", choices=["lower", "higher"],
                        default="lower",
                        help="Whether lower or higher metric is better")
    parser.add_argument("--baseline", type=float,
                        help="Baseline metric value for delta calculation")
    parser.add_argument("--diff-summary", action="store_true",
                        help="Show diff statistics per agent (no eval cmd needed)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--demo", action="store_true",
                        help="Show demo output")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if not args.session:
        print("Error: --session is required", file=sys.stderr)
        sys.exit(1)

    config = get_session_config(args.session)
    branches = get_hub_branches(args.session)

    if not branches:
        print(f"No branches found for session {args.session}")
        return

    eval_cmd = args.eval_cmd or config.get("eval_cmd")
    metric = args.metric or config.get("metric")
    direction = args.direction or config.get("direction", "lower")
    base_branch = config.get("base_branch", "main")

    results = []
    for branch in branches:
        # Extract agent number
        match = re.match(r"hub/[^/]+/agent-(\d+)/", branch)
        agent_id = f"agent-{match.group(1)}" if match else branch.split("/")[-2]

        result = {
            "agent": agent_id,
            "branch": branch,
            "metric_value": None,
            "metric_raw": None,
            "diff": get_diff_stats(branch, base_branch),
        }

        if eval_cmd and metric:
            worktree = get_worktree_path(branch)
            if worktree:
                output, returncode = run_eval_in_worktree(worktree, eval_cmd)
                result["metric_raw"] = output
                result["eval_returncode"] = returncode
                if returncode == 0:
                    result["metric_value"] = extract_metric(output, metric)

        results.append(result)

    # Rank
    ranked = rank_by_metric(results, direction)

    # Calculate deltas
    baseline = args.baseline
    if baseline is None and ranked and ranked[0].get("metric_value") is not None:
        # Use worst as baseline if not specified
        values = [r["metric_value"] for r in ranked if r["metric_value"] is not None]
        if values:
            baseline = max(values) if direction == "lower" else min(values)

    for r in ranked:
        if r.get("metric_value") is not None and baseline is not None:
            r["delta"] = r["metric_value"] - baseline
        else:
            r["delta"] = None

    if args.format == "json":
        print(json.dumps({"session": args.session, "results": ranked}, indent=2))
        return

    # Table output
    print(f"Session: {args.session}")
    if eval_cmd:
        print(f"Eval: {eval_cmd}")
    if metric:
        dir_str = "lower is better" if direction == "lower" else "higher is better"
        print(f"Metric: {metric} ({dir_str})")
    if baseline:
        print(f"Baseline: {baseline}")
    print()

    if args.diff_summary or not eval_cmd:
        header = f"{'RANK':<6} {'AGENT':<12} {'FILES':<7} {'ADDED':<8} {'REMOVED':<8} {'NET':<6}"
        print(header)
        print("-" * 50)
        for i, r in enumerate(ranked):
            d = r["diff"]
            print(f"{i+1:<6} {r['agent']:<12} {d['files_changed']:<7} "
                  f"+{d['insertions']:<7} -{d['deletions']:<7} {d['net_lines']:<6}")
    else:
        header = f"{'RANK':<6} {'AGENT':<12} {'METRIC':<12} {'DELTA':<10} {'FILES':<7}"
        print(header)
        print("-" * 50)
        for r in ranked:
            mv = str(r["metric_value"]) if r["metric_value"] is not None else "N/A"
            delta = ""
            if r["delta"] is not None:
                sign = "+" if r["delta"] >= 0 else ""
                delta = f"{sign}{r['delta']:.1f}"
            print(f"{r['rank']:<6} {r['agent']:<12} {mv:<12} {delta:<10} {r['diff']['files_changed']:<7}")

    # Winner
    if ranked and ranked[0].get("metric_value") is not None:
        winner = ranked[0]
        print()
        print(f"Winner: {winner['agent']} ({winner['metric_value']})")

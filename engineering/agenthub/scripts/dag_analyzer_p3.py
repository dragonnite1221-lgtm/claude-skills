# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dag_analyzer_base import *  # noqa: F403,E402
# fmt: off
from dag_analyzer_p1 import detect_frontier, show_graph  # noqa: E402,E501
from dag_analyzer_p2 import run_demo, show_status  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Analyze the AgentHub git DAG"
    )
    parser.add_argument("--frontier", action="store_true",
                        help="List frontier branches (leaves with no children)")
    parser.add_argument("--graph", action="store_true",
                        help="Show ASCII DAG graph for hub branches")
    parser.add_argument("--status", action="store_true",
                        help="Show per-agent branch status")
    parser.add_argument("--session", type=str,
                        help="Filter by session ID")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                        help="Output format (default: table)")
    parser.add_argument("--demo", action="store_true",
                        help="Show demo output")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if not any([args.frontier, args.graph, args.status]):
        parser.print_help()
        return

    if args.frontier:
        frontier = detect_frontier(args.session)
        if args.format == "json":
            print(json.dumps({"frontier": frontier}, indent=2))
        else:
            if frontier:
                print("Frontier branches:")
                for b in frontier:
                    print(f"  {b}")
            else:
                print("No frontier branches found.")
        print()

    if args.graph:
        show_graph()
        print()

    if args.status:
        if not args.session:
            print("Error: --session required with --status", file=sys.stderr)
            sys.exit(1)
        show_status(args.session, args.format)

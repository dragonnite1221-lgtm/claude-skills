# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from session_manager_base import *  # noqa: F403,E402
# fmt: off
from session_manager_p1 import list_sessions, show_status  # noqa: E402,E501
from session_manager_p2 import cleanup_session, run_demo, update_state  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="AgentHub session state machine and lifecycle manager"
    )
    parser.add_argument("--list", action="store_true",
                        help="List all sessions with state")
    parser.add_argument("--status", type=str, metavar="SESSION_ID",
                        help="Show detailed session status")
    parser.add_argument("--update", type=str, metavar="SESSION_ID",
                        help="Update session state")
    parser.add_argument("--state", type=str,
                        help="New state for --update")
    parser.add_argument("--cleanup", type=str, metavar="SESSION_ID",
                        help="Remove worktrees and clean up session")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--demo", action="store_true",
                        help="Show demo output")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.list:
        list_sessions(args.format)
        return

    if args.status:
        show_status(args.status, args.format)
        return

    if args.update:
        if not args.state:
            print("Error: --update requires --state", file=sys.stderr)
            sys.exit(1)
        update_state(args.update, args.state)
        return

    if args.cleanup:
        cleanup_session(args.cleanup)
        return

    parser.print_help()

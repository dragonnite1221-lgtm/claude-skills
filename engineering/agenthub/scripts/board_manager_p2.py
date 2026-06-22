# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from board_manager_base import *  # noqa: F403,E402
# fmt: off
from board_manager_p1 import create_post, list_channels, read_channel  # noqa: E402,E501
# fmt: on


def run_demo():
    """Show demo output."""
    print("=" * 60)
    print("AgentHub Board Manager — Demo Mode")
    print("=" * 60)
    print()

    print("--- Channel List ---")
    print("Board Channels:")
    print()
    print("  dispatch        2 posts")
    print("  progress        4 posts")
    print("  results         3 posts")
    print()

    print("--- Read Channel: results ---")
    print("Channel: results (3 posts)")
    print("=" * 60)
    print()
    print("--- 001-agent-1-20260317T143510Z.md (by agent-1, 2026-03-17T14:35:10Z) ---")
    print("## Result Summary")
    print()
    print("- **Approach**: Added caching layer for database queries")
    print("- **Files changed**: 3")
    print("- **Metric**: 165ms (baseline: 180ms, delta: -15ms)")
    print("- **Confidence**: Medium — 2 edge cases not covered")
    print()
    print("--- 002-agent-2-20260317T143645Z.md (by agent-2, 2026-03-17T14:36:45Z) ---")
    print("## Result Summary")
    print()
    print("- **Approach**: Replaced O(n²) sort with hash map lookup")
    print("- **Files changed**: 2")
    print("- **Metric**: 142ms (baseline: 180ms, delta: -38ms)")
    print("- **Confidence**: High — all tests pass")
    print()
    print("--- 003-agent-3-20260317T143422Z.md (by agent-3, 2026-03-17T14:34:22Z) ---")
    print("## Result Summary")
    print()
    print("- **Approach**: Minor loop optimizations")
    print("- **Files changed**: 1")
    print("- **Metric**: 190ms (baseline: 180ms, delta: +10ms)")
    print("- **Confidence**: Low — no meaningful improvement")
def main():
    parser = argparse.ArgumentParser(
        description="AgentHub message board manager"
    )
    parser.add_argument("--list", action="store_true",
                        help="List all channels with post counts")
    parser.add_argument("--read", type=str, metavar="CHANNEL",
                        help="Read all posts in a channel")
    parser.add_argument("--post", action="store_true",
                        help="Create a new post")
    parser.add_argument("--channel", type=str,
                        help="Channel for --post or --thread")
    parser.add_argument("--author", type=str,
                        help="Author name for --post")
    parser.add_argument("--message", type=str,
                        help="Message content for --post or --thread")
    parser.add_argument("--thread", type=str, metavar="POST_ID",
                        help="Reply to a post (sets parent)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--demo", action="store_true",
                        help="Show demo output")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.list:
        list_channels(args.format)
        return

    if args.read:
        read_channel(args.read, args.format)
        return

    if args.post:
        if not args.channel or not args.author or not args.message:
            print("Error: --post requires --channel, --author, and --message",
                  file=sys.stderr)
            sys.exit(1)
        create_post(args.channel, args.author, args.message)
        return

    if args.thread:
        if not args.message:
            print("Error: --thread requires --message", file=sys.stderr)
            sys.exit(1)
        channel = args.channel or "results"
        author = args.author or "coordinator"
        create_post(channel, author, args.message, parent=args.thread)
        return

    parser.print_help()

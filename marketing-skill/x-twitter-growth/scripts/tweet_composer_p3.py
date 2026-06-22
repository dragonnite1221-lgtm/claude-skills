# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tweet_composer_base import *  # noqa: F403,E402
# fmt: off
from tweet_composer_p1 import MAX_TWEET_CHARS, validate_tweet  # noqa: E402,E501
from tweet_composer_p2 import generate_hooks, generate_thread_outline  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate tweets, threads, and hooks with proven patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--type", choices=["tweet", "thread", "hooks", "validate"],
                        default="hooks", help="Content type to generate")
    parser.add_argument("--topic", default="", help="Topic for content generation")
    parser.add_argument("--tweets", type=int, default=8, help="Number of tweets in thread")
    parser.add_argument("--count", type=int, default=10, help="Number of hooks to generate")
    parser.add_argument("--validate", nargs="?", const="", help="Tweet text to validate")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.type == "validate" or args.validate is not None:
        text = args.validate or args.topic
        if not text:
            print("Error: provide tweet text to validate", file=sys.stderr)
            sys.exit(1)
        result = validate_tweet(text)
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            icon = "🔴" if result.over_limit else "✅"
            print(f"\n  {icon} {result.char_count}/{MAX_TWEET_CHARS} characters")
            if result.warnings:
                for w in result.warnings:
                    print(f"  ⚠️  {w}")
            else:
                print("  No issues found.")
            print()

    elif args.type == "hooks":
        if not args.topic:
            print("Error: --topic required for hook generation", file=sys.stderr)
            sys.exit(1)
        hooks = generate_hooks(args.topic, args.count)
        if args.json:
            print(json.dumps(hooks, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  HOOK IDEAS: {args.topic}")
            print(f"{'='*60}\n")
            for i, h in enumerate(hooks, 1):
                print(f"  {i:2d}. [{h['type']:<12}] {h['hook']}")
                print(f"      ({h['chars']} chars)")
            print()

    elif args.type == "thread":
        if not args.topic:
            print("Error: --topic required for thread generation", file=sys.stderr)
            sys.exit(1)
        outline = generate_thread_outline(args.topic, args.tweets)
        print(outline)

    elif args.type == "tweet":
        if not args.topic:
            print("Error: --topic required", file=sys.stderr)
            sys.exit(1)
        hooks = generate_hooks(args.topic, 5)
        print(f"\n  5 tweet drafts for: {args.topic}\n")
        for i, h in enumerate(hooks, 1):
            print(f"  {i}. {h['hook']}")
            print(f"     ({h['chars']} chars)\n")

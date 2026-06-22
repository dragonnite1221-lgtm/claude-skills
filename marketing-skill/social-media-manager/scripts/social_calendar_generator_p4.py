# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from social_calendar_generator_base import *  # noqa: F403,E402
# fmt: off
from social_calendar_generator_p1 import DEMO_CONFIG  # noqa: E402,E501
from social_calendar_generator_p2 import build_calendar  # noqa: E402,E501
from social_calendar_generator_p3 import build_markdown, pretty_print  # noqa: E402,E501
# fmt: on


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a social media content calendar with balanced pillar distribution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config",   type=str, default=None,
                        help="Path to JSON config file")
    parser.add_argument("--start",    type=str, default=None,
                        help="Start date YYYY-MM-DD (overrides config)")
    parser.add_argument("--weeks",    type=int, default=None,
                        help="Number of weeks to generate (overrides config)")
    parser.add_argument("--json",     action="store_true",
                        help="Output calendar as JSON")
    parser.add_argument("--markdown", action="store_true",
                        help="Output calendar as Markdown")
    return parser.parse_args()
def main():
    args = parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        print("🔬  DEMO MODE — using sample config (4 pillars, 2 platforms)\n",
              file=sys.stderr)
        config = dict(DEMO_CONFIG)

    # CLI overrides
    if args.start:
        config["start_date"] = args.start
    if args.weeks:
        config["weeks"] = args.weeks

    result = build_calendar(config)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    elif args.markdown:
        print(build_markdown(result))
    else:
        pretty_print(result)

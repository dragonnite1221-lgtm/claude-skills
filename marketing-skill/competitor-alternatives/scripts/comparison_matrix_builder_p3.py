# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comparison_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from comparison_matrix_builder_p1 import build_matrix  # noqa: E402,E501
from comparison_matrix_builder_p2 import DEMO_DATA, build_markdown, pretty_print  # noqa: E402,E501
# fmt: on


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a competitive feature comparison matrix (stdlib only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input",    type=str, default=None,
                        help="Path to JSON input file")
    parser.add_argument("--json",     action="store_true",
                        help="Output analysis as JSON")
    parser.add_argument("--markdown", action="store_true",
                        help="Output comparison table as Markdown")
    return parser.parse_args()
def main():
    args = parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        print("🔬  DEMO MODE — using sample SaaS product matrix\n", file=sys.stderr)
        data = DEMO_DATA

    result = build_matrix(data)

    if args.json:
        # Serialise (remove non-JSON-safe keys)
        print(json.dumps(result, indent=2))
    elif args.markdown:
        print(build_markdown(result))
    else:
        pretty_print(result)
        print("\n💡  TIP: Re-run with --markdown to get a copyable Markdown table.\n")

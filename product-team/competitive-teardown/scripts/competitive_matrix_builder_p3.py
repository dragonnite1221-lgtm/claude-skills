# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from competitive_matrix_builder_p1 import load_competitors  # noqa: E402,E501
from competitive_matrix_builder_p2 import build_matrix, format_text, parse_weights  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Build competitive matrix with scoring and gap analysis"
    )
    parser.add_argument("input", help="Path to competitors JSON file")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    parser.add_argument("--weights", type=str, default=None,
                       help="Weight overrides: 'dim1=2.0,dim2=1.5'")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file path (default: stdout)")

    args = parser.parse_args()

    data = load_competitors(args.input)
    weight_overrides = parse_weights(args.weights) if args.weights else None
    result = build_matrix(data, weight_overrides)

    if args.format == "json":
        output = json.dumps(result, indent=2)
    else:
        output = format_text(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)

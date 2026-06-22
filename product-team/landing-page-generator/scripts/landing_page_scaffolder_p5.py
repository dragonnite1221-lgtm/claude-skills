# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from landing_page_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from landing_page_scaffolder_p3 import generate_tsx  # noqa: E402,E501
from landing_page_scaffolder_p4 import generate_html  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate landing pages as HTML or Next.js TSX with Tailwind CSS"
    )
    parser.add_argument("input", help="Path to page config JSON")
    parser.add_argument(
        "--format", choices=["html", "tsx", "json"], default="tsx",
        help="Output format: tsx (Next.js + Tailwind), html (standalone), json (metadata)"
    )
    parser.add_argument("--output", type=str, default=None, help="Output file path")

    args = parser.parse_args()

    with open(args.input) as f:
        config = json.load(f)

    if args.format == "json":
        output = json.dumps({
            "generated_at": datetime.now().isoformat(),
            "config": config,
            "formats_available": ["html", "tsx"],
            "sections": [k for k in ["nav", "hero", "features", "testimonials", "pricing", "cta", "footer"]
                         if config.get(k) or k in ("nav", "footer")]
        }, indent=2)
    elif args.format == "tsx":
        output = generate_tsx(config)
    else:
        output = generate_html(config)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Landing page written to {args.output}")
    else:
        print(output)

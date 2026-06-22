# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from design_token_generator_base import *  # noqa: F403,E402


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Design Token Generator - Creates consistent design system tokens for colors, typography, spacing, and more."
    )
    parser.add_argument(
        "brand_color", nargs="?", default="#0066CC",
        help="Hex brand color (default: #0066CC)"
    )
    parser.add_argument(
        "--style", choices=["modern", "classic", "playful"], default="modern",
        help="Design style (default: modern)"
    )
    parser.add_argument(
        "--format", choices=["json", "css", "scss", "summary"], default="json",
        dest="output_format",
        help="Output format (default: json)"
    )
    args = parser.parse_args()

    generator = DesignTokenGenerator()
    tokens = generator.generate_complete_system(args.brand_color, args.style)

    if args.output_format == 'summary':
        print("=" * 60)
        print("DESIGN SYSTEM TOKENS")
        print("=" * 60)
        print(f"\n  Style: {args.style}")
        print(f"  Brand Color: {args.brand_color}")
        print("\n  Generated Tokens:")
        print(f"  - Colors: {len(tokens['colors'])} palettes")
        print(f"  - Typography: {len(tokens['typography'])} categories")
        print(f"  - Spacing: {len(tokens['spacing'])} values")
        print(f"  - Shadows: {len(tokens['shadows'])} styles")
        print(f"  - Breakpoints: {len(tokens['breakpoints'])} sizes")
        print("\n  Export formats available: json, css, scss")
    else:
        print(generator.export_tokens(tokens, args.output_format))

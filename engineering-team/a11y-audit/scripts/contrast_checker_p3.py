# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from contrast_checker_base import *  # noqa: F403,E402
# fmt: off
from contrast_checker_p1 import color_to_hex, contrast_ratio, evaluate_contrast, parse_color  # noqa: E402,E501
from contrast_checker_p2 import DEMO_PAIRS, format_result_human, format_suggestions_human, suggest_backgrounds  # noqa: E402,E501
# fmt: on


def run_demo(as_json: bool) -> None:
    """Run demo checks and print results."""
    all_results = []
    for fg_str, bg_str in DEMO_PAIRS:
        fg_rgb = parse_color(fg_str)
        bg_rgb = parse_color(bg_str)
        ratio = contrast_ratio(fg_rgb, bg_rgb)
        results = evaluate_contrast(ratio)
        entry = {
            "foreground": fg_str,
            "background": bg_str,
            "foreground_hex": color_to_hex(fg_rgb),
            "background_hex": color_to_hex(bg_rgb),
            "ratio": round(ratio, 2),
            "results": results,
        }
        all_results.append(entry)

    if as_json:
        print(json.dumps({"demo": True, "checks": all_results}, indent=2))
    else:
        print("=" * 60)
        print("WCAG 2.2 Contrast Checker - Demo")
        print("=" * 60)
        for entry in all_results:
            print()
            print(
                format_result_human(
                    entry["foreground"], entry["background"],
                    entry["ratio"], entry["results"],
                )
            )
        print()
        print("-" * 60)
        print("Suggestion demo for foreground #336699:")
        suggestions = suggest_backgrounds(parse_color("#336699"))
        print(format_suggestions_human("#336699", suggestions))
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WCAG 2.2 Color Contrast Checker. "
        "Checks foreground/background pairs against AA and AAA thresholds.",
        epilog="Examples:\n"
        "  %(prog)s '#ffffff' '#000000'\n"
        "  %(prog)s --suggest '#336699'\n"
        "  %(prog)s --batch styles.css\n"
        "  %(prog)s --demo\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "foreground",
        nargs="?",
        help="Foreground (text) color: #RRGGBB, #RGB, rgb(r,g,b), or named color",
    )
    parser.add_argument(
        "background",
        nargs="?",
        help="Background color: #RRGGBB, #RGB, rgb(r,g,b), or named color",
    )
    parser.add_argument(
        "--suggest",
        metavar="COLOR",
        help="Suggest accessible background colors for the given foreground color",
    )
    parser.add_argument(
        "--batch",
        metavar="CSS_FILE",
        help="Extract color pairs from a CSS file and check each",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show example output with sample color pairs",
    )
    return parser

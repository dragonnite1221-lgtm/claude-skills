# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from contrast_checker_base import *  # noqa: F403,E402
# fmt: off
from contrast_checker_p1 import color_to_hex, contrast_ratio, evaluate_contrast, parse_color  # noqa: E402,E501
from contrast_checker_p2 import extract_css_pairs, format_result_human, format_suggestions_human, suggest_backgrounds  # noqa: E402,E501
from contrast_checker_p3 import build_parser, run_demo  # noqa: E402,E501
# fmt: on


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # --demo mode
    if args.demo:
        run_demo(args.json_output)
        return 0

    # --suggest mode
    if args.suggest:
        try:
            fg_rgb = parse_color(args.suggest)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        suggestions = suggest_backgrounds(fg_rgb)
        if args.json_output:
            print(json.dumps({
                "foreground": args.suggest,
                "foreground_hex": color_to_hex(fg_rgb),
                "suggestions": suggestions,
            }, indent=2))
        else:
            print(format_suggestions_human(args.suggest, suggestions))
        return 0

    # --batch mode
    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as fh:
                css_text = fh.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.batch}", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 1

        pairs = extract_css_pairs(css_text)
        if not pairs:
            msg = "No color/background-color pairs found in the CSS file."
            if args.json_output:
                print(json.dumps({"batch": args.batch, "pairs": [], "message": msg}, indent=2))
            else:
                print(msg)
            return 0

        all_results = []
        has_failure = False
        for pair in pairs:
            try:
                fg_rgb = parse_color(pair["foreground"])
                bg_rgb = parse_color(pair["background"])
            except ValueError as exc:
                entry = {
                    "selector": pair["selector"],
                    "foreground": pair["foreground"],
                    "background": pair["background"],
                    "error": str(exc),
                }
                all_results.append(entry)
                continue

            ratio = contrast_ratio(fg_rgb, bg_rgb)
            results = evaluate_contrast(ratio)
            if not results[0]["pass"]:  # AA Normal Text
                has_failure = True
            entry = {
                "selector": pair["selector"],
                "foreground": pair["foreground"],
                "background": pair["background"],
                "foreground_hex": color_to_hex(fg_rgb),
                "background_hex": color_to_hex(bg_rgb),
                "ratio": round(ratio, 2),
                "results": results,
            }
            all_results.append(entry)

        if args.json_output:
            print(json.dumps({"batch": args.batch, "pairs": all_results}, indent=2))
        else:
            print(f"Batch check: {args.batch}")
            print("=" * 60)
            for entry in all_results:
                print(f"\nSelector: {entry['selector']}")
                if "error" in entry:
                    print(f"  Error: {entry['error']}")
                else:
                    print(
                        format_result_human(
                            entry["foreground"], entry["background"],
                            entry["ratio"], entry["results"],
                        )
                    )
            print()
            summary_pass = sum(1 for e in all_results if "ratio" in e and e["results"][0]["pass"])
            summary_total = sum(1 for e in all_results if "ratio" in e)
            print(f"Summary: {summary_pass}/{summary_total} pairs pass AA Normal Text")

        return 1 if has_failure else 0

    # Default: check a single pair
    if not args.foreground or not args.background:
        parser.error(
            "Provide foreground and background colors, or use --suggest, --batch, or --demo."
        )

    try:
        fg_rgb = parse_color(args.foreground)
    except ValueError as exc:
        print(f"Error (foreground): {exc}", file=sys.stderr)
        return 1

    try:
        bg_rgb = parse_color(args.background)
    except ValueError as exc:
        print(f"Error (background): {exc}", file=sys.stderr)
        return 1

    ratio = contrast_ratio(fg_rgb, bg_rgb)
    results = evaluate_contrast(ratio)

    if args.json_output:
        print(json.dumps({
            "foreground": args.foreground,
            "background": args.background,
            "foreground_hex": color_to_hex(fg_rgb),
            "background_hex": color_to_hex(bg_rgb),
            "ratio": round(ratio, 2),
            "results": results,
        }, indent=2))
    else:
        print(format_result_human(args.foreground, args.background, ratio, results))

    return 0 if results[0]["pass"] else 1

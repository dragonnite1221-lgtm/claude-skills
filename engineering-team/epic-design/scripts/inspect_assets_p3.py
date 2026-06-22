# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inspect_assets_base import *  # noqa: F403,E402


def print_report(results):
    print("\n" + "═" * 55)
    print("  2.5D Asset Inspector Report")
    print("═" * 55)

    for r in results:
        print(f"\n📁  {r['filename']}")
        print(f"    Format : {r['format']}  |  Mode: {r['mode']}  |  Size: {r['size']}")

        status_icons = {
            "CLEAN": "✅",
            "DARK_BG": "⚠️ ",
            "LIGHT_BG": "⚠️ ",
            "COMPLEX_BG": "🔵",
            "MIDTONE_BG": "❓",
            "UNKNOWN": "❓",
            "ERROR": "❌",
        }
        icon = status_icons.get(r["status"], "❓")
        print(f"    Status : {icon}  {r['status']}")

        if r["bg_type"]:
            print(f"    Bg type: {r['bg_type']}")

        if r["likely_needs_removal"] is True:
            print("    Removal: Likely needed (product/object shot)")
        elif r["likely_needs_removal"] is False:
            print("    Removal: Likely NOT needed (scene/artwork/content image)")
        else:
            print("    Removal: Ambiguous — AI must judge from context")

        for note in r["notes"]:
            print(f"    → {note}")

    print("\n" + "═" * 55)
    clean = sum(1 for r in results if r["status"] == "CLEAN")
    flagged = sum(1 for r in results if r["status"] in ("DARK_BG", "LIGHT_BG", "MIDTONE_BG"))
    complex_bg = sum(1 for r in results if r["status"] == "COMPLEX_BG")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"  Clean: {clean}  |  Flagged: {flagged}  |  Complex/Scene: {complex_bg}  |  Errors: {errors}")
    print("═" * 55)
    print("\nNext step: Read JUDGMENT notes above and inform the user.")
    print("See references/asset-pipeline.md for the exact notification format.\n")
def collect_paths(args):
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            for f in os.listdir(arg):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".avif")):
                    paths.append(os.path.join(arg, f))
        elif os.path.isfile(arg):
            paths.append(arg)
        else:
            print(f"⚠️  Not found: {arg}")
    return paths

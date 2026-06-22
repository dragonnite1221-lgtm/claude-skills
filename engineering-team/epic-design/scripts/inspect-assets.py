# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inspect_assets_base import *  # noqa: F403,E402


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("\nUsage:")
        print("  python scripts/inspect-assets.py image.png")
        print("  python scripts/inspect-assets.py image1.jpg image2.png")
        print("  python scripts/inspect-assets.py path/to/folder/\n")
        if len(sys.argv) < 2:
            sys.exit(1)
        else:
            sys.exit(0)

    paths = collect_paths(sys.argv[1:])
    if not paths:
        print("No valid image files found.")
        sys.exit(1)

    results = [analyse_image(p) for p in paths]
    print_report(results)

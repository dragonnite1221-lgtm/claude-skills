# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dry_run_base import *  # noqa: F403,E402
# fmt: off
from dry_run_p1 import PLUGIN_ROOT, Results, check_frontmatter, check_json  # noqa: E402,E501
from dry_run_p2 import check_cross_domain, check_markdown, check_references, check_scripts  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Dry-run validation for the AgentHub plugin."
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-file check details")
    args = parser.parse_args()

    print(f"AgentHub dry-run validation")
    print(f"Plugin root: {PLUGIN_ROOT}\n")

    all_ok = True
    sections = [
        ("JSON validity", check_json),
        ("YAML frontmatter", check_frontmatter),
        ("Markdown structure", check_markdown),
        ("Script --help", check_scripts),
        ("Referenced files", check_references),
        ("Cross-domain examples", check_cross_domain),
    ]

    for title, fn in sections:
        print(f"── {title} ──")
        r = Results()
        fn(r)
        ok = r.print(verbose=args.verbose)
        if not ok:
            all_ok = False
        print()

    if all_ok:
        print("\033[32mAll checks passed.\033[0m")
    else:
        print("\033[31mSome checks failed — see above.\033[0m")
        sys.exit(1)

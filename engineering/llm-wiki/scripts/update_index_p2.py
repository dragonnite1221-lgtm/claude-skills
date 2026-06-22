# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from update_index_base import *  # noqa: F403,E402
# fmt: off
from update_index_p1 import render_index, scan_wiki  # noqa: E402,E501
# fmt: on


def main():
    p = argparse.ArgumentParser(
        description="Regenerate wiki/index.md from every wiki page's YAML frontmatter.",
        epilog="The index is organized by category (synthesis, concept, entity, source, comparison).",
    )
    p.add_argument("--vault", required=True, help="Vault root directory")
    p.add_argument(
        "--dry-run", action="store_true", help="Print to stdout instead of writing"
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON summary of the regeneration result",
    )
    args = p.parse_args()

    try:
        vault = Path(args.vault).expanduser().resolve()
        pages = scan_wiki(vault)
        content = render_index(pages, vault.name)
    except SystemExit:
        raise
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)

    total = sum(len(v) for v in pages.values())
    summary = {
        "status": "ok",
        "vault": str(vault),
        "total_pages": total,
        "by_category": {k: len(v) for k, v in pages.items()},
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        if args.json:
            summary["content_preview"] = content[:500]
            print(json.dumps(summary, indent=2))
        else:
            print(content)
        return

    index_path = vault / "wiki" / "index.md"
    try:
        index_path.write_text(content, encoding="utf-8")
    except OSError as e:
        if args.json:
            print(json.dumps({"status": "error", "message": f"failed to write {index_path}: {e}"}))
        else:
            print(f"[error] failed to write {index_path}: {e}", file=sys.stderr)
        sys.exit(1)

    summary["index_path"] = str(index_path)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"[ok] wrote {index_path} ({total} pages)")

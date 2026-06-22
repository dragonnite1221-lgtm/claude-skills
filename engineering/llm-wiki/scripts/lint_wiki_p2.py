# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from lint_wiki_base import *  # noqa: F403,E402
# fmt: off
from lint_wiki_p1 import scan  # noqa: E402,E501
# fmt: on


def print_report(r: dict) -> None:
    print(f"LLM Wiki health check — {r['vault']}")
    print(f"Total pages: {r['total_pages']}")
    print()

    def header(label: str, count: int) -> None:
        sym = "OK" if count == 0 else "WARN"
        print(f"[{sym}] {label}: {count}")

    header("orphan pages", len(r["orphans"]))
    for p in r["orphans"][:20]:
        print(f"   - {p}")
    if len(r["orphans"]) > 20:
        print(f"   ... and {len(r['orphans']) - 20} more")
    print()

    header("broken wikilinks", len(r["broken_links"]))
    for src, tgt in r["broken_links"][:20]:
        print(f"   - {src} -> [[{tgt}]]")
    print()

    header("stale pages", len(r["stale"]))
    for p, d in r["stale"][:20]:
        print(f"   - {p} (updated {d})")
    print()

    header("pages missing frontmatter", len(r["missing_frontmatter"]))
    for p in r["missing_frontmatter"][:20]:
        print(f"   - {p}")
    print()

    header("duplicate titles", len(r["duplicate_titles"]))
    for title, keys in list(r["duplicate_titles"].items())[:10]:
        print(f"   - '{title}': {keys}")
    print()

    gap = r["log_gap"]
    if gap:
        print(f"[WARN] log gap: last entry {gap['last_entry']} ({gap['days_ago']} days ago)")
    else:
        print("[OK] log gap: recent")
def main() -> None:
    p = argparse.ArgumentParser(description="Lint an LLM Wiki vault")
    p.add_argument("--vault", required=True)
    p.add_argument("--stale-days", type=int, default=90)
    p.add_argument("--log-gap-days", type=int, default=14)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    report = scan(
        Path(args.vault).expanduser().resolve(),
        stale_days=args.stale_days,
        log_gap_days=args.log_gap_days,
    )
    if args.json:
        print(json.dumps(report, indent=2, default=list))
    else:
        print_report(report)

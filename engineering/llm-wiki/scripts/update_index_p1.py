# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from update_index_base import *  # noqa: F403,E402


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
CATEGORY_ORDER = ["synthesis", "concept", "entity", "source", "comparison", "other"]
CATEGORY_DIRS = {
    "entities": "entity",
    "concepts": "concept",
    "sources": "source",
    "comparisons": "comparison",
    "synthesis": "synthesis",
}
def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    raw = m.group(1)
    fm: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip("'\"")
    return fm
def infer_title(path: Path, fm: dict[str, str]) -> str:
    if "title" in fm:
        return fm["title"]
    return path.stem.replace("-", " ").replace("_", " ").title()
def scan_wiki(vault: Path) -> dict[str, list[dict]]:
    wiki = vault / "wiki"
    if not wiki.exists():
        print(f"[error] {wiki} not found", file=sys.stderr)
        sys.exit(1)

    pages: dict[str, list[dict]] = defaultdict(list)
    for md in sorted(wiki.rglob("*.md")):
        # Skip index, log, and template files
        rel = md.relative_to(wiki)
        if rel.name in {"index.md", "log.md"}:
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue

        text = md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)

        # Category: prefer frontmatter, fall back to folder name
        category = fm.get("category")
        if not category and len(rel.parts) > 1:
            folder = rel.parts[0]
            category = CATEGORY_DIRS.get(folder, "other")
        category = category or "other"

        pages[category].append(
            {
                "path": str(rel).replace("\\", "/"),
                "title": infer_title(md, fm),
                "summary": fm.get("summary", ""),
                "tags": fm.get("tags", ""),
                "sources": fm.get("sources", ""),
                "updated": fm.get("updated", ""),
            }
        )

    # Sort each category by title
    for cat in pages:
        pages[cat].sort(key=lambda p: p["title"].lower())
    return pages
def render_index(pages: dict[str, list[dict]], vault_name: str) -> str:
    today = dt.date.today().isoformat()
    total = sum(len(v) for v in pages.values())

    lines = [
        f"# Index — {vault_name}",
        "",
        f"_Auto-generated {today} • {total} pages_",
        "",
        "> Content-oriented catalog of every page in `wiki/`. Updated by",
        "> `scripts/update_index.py` or during `/wiki-ingest`. Answer queries",
        "> by reading this file first, then drilling into relevant pages.",
        "",
    ]

    for cat in CATEGORY_ORDER:
        entries = pages.get(cat, [])
        if not entries:
            continue
        lines.append(f"## {cat.capitalize()} ({len(entries)})")
        lines.append("")
        for e in entries:
            summary = f" — {e['summary']}" if e["summary"] else ""
            link = f"[[{e['path'][:-3]}|{e['title']}]]"  # Obsidian wikilink, strip .md
            meta = []
            if e["sources"]:
                meta.append(f"{e['sources']} sources")
            if e["updated"]:
                meta.append(f"upd {e['updated']}")
            meta_str = f" _({' · '.join(meta)})_" if meta else ""
            lines.append(f"- {link}{summary}{meta_str}")
        lines.append("")

    return "\n".join(lines)

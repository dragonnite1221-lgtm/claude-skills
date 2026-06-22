# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from lint_wiki_base import *  # noqa: F403,E402


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
LOG_ENTRY_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\]", re.MULTILINE)
def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip("'\"")
    return fm
def scan(vault: Path, stale_days: int, log_gap_days: int) -> dict:
    wiki = vault / "wiki"
    if not wiki.exists():
        raise SystemExit(f"[error] {wiki} not found")

    pages: dict[str, dict] = {}
    inbound: dict[str, set[str]] = defaultdict(set)
    outbound: dict[str, set[str]] = defaultdict(set)

    for md in wiki.rglob("*.md"):
        rel = md.relative_to(wiki)
        if rel.name in {"index.md", "log.md"}:
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        key = str(rel).replace("\\", "/")[:-3]  # strip .md
        text = md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        pages[key] = {"path": key + ".md", "fm": fm, "text": text}

    # Build link graph
    stems = {Path(k).name: k for k in pages}
    for key, page in pages.items():
        for m in WIKILINK_RE.finditer(page["text"]):
            target = m.group(1).strip()
            # Normalize: strip .md, try full path match first, then stem
            if target.endswith(".md"):
                target = target[:-3]
            if target in pages:
                outbound[key].add(target)
                inbound[target].add(key)
            elif Path(target).name in stems:
                resolved = stems[Path(target).name]
                outbound[key].add(resolved)
                inbound[resolved].add(key)
            else:
                outbound[key].add(f"__BROKEN__:{target}")

    today = dt.date.today()
    stale_cutoff = today - dt.timedelta(days=stale_days)

    orphans = sorted(k for k in pages if not inbound.get(k))
    broken_links: list[tuple[str, str]] = []
    for src, targets in outbound.items():
        for t in targets:
            if t.startswith("__BROKEN__:"):
                broken_links.append((src, t.split(":", 1)[1]))
    broken_links.sort()

    stale: list[tuple[str, str]] = []
    missing_fm: list[str] = []
    titles: dict[str, list[str]] = defaultdict(list)
    for key, page in pages.items():
        fm = page["fm"]
        title = fm.get("title") or Path(key).name
        titles[title].append(key)
        required = {"title", "category", "summary"}
        if not required.issubset(fm.keys()):
            missing_fm.append(key)
        updated = fm.get("updated")
        if updated:
            try:
                d = dt.date.fromisoformat(updated)
                if d < stale_cutoff:
                    stale.append((key, updated))
            except ValueError:
                pass
    duplicate_titles = {t: ks for t, ks in titles.items() if len(ks) > 1}

    # Log gap check
    log_path = wiki / "log.md"
    log_gap = None
    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        dates = [dt.date.fromisoformat(m) for m in LOG_ENTRY_RE.findall(log_text)]
        if dates:
            last = max(dates)
            gap = (today - last).days
            if gap > log_gap_days:
                log_gap = {"last_entry": last.isoformat(), "days_ago": gap}
        else:
            log_gap = {"last_entry": None, "days_ago": None}

    return {
        "vault": str(vault),
        "total_pages": len(pages),
        "orphans": orphans,
        "broken_links": broken_links,
        "stale": stale,
        "missing_frontmatter": sorted(missing_fm),
        "duplicate_titles": duplicate_titles,
        "log_gap": log_gap,
    }

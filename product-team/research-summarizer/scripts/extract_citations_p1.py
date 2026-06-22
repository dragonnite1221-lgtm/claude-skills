# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from extract_citations_base import *  # noqa: F403,E402


PATTERNS = {
    "doi": re.compile(
        r"(?:https?://doi\.org/|doi:\s*)(10\.\d{4,}/[^\s,;}\]]+)", re.IGNORECASE
    ),
    "url": re.compile(
        r"https?://[^\s,;}\])\"'>]+", re.IGNORECASE
    ),
    "author_year": re.compile(
        r"(?:^|\(|\s)([A-Z][a-z]+(?:\s(?:&|and)\s[A-Z][a-z]+)?(?:\set\sal\.?)?)\s*\((\d{4})\)",
    ),
    "numbered_ref": re.compile(
        r"^\[(\d+)\]\s+(.+)$", re.MULTILINE
    ),
    "footnote": re.compile(
        r"^\d+\.\s+([A-Z].+?(?:\d{4}).+)$", re.MULTILINE
    ),
}
def extract_dois(text):
    """Extract DOI references."""
    citations = []
    for match in PATTERNS["doi"].finditer(text):
        doi = match.group(1).rstrip(".")
        citations.append({
            "type": "doi",
            "doi": doi,
            "raw": match.group(0).strip(),
            "url": f"https://doi.org/{doi}",
        })
    return citations
def extract_urls(text):
    """Extract URL references (excluding DOI URLs already captured)."""
    citations = []
    for match in PATTERNS["url"].finditer(text):
        url = match.group(0).rstrip(".,;)")
        if "doi.org" in url:
            continue
        citations.append({
            "type": "url",
            "url": url,
            "raw": url,
        })
    return citations
def extract_author_year(text):
    """Extract author-year citations like (Smith, 2023) or Smith & Jones (2021)."""
    citations = []
    for match in PATTERNS["author_year"].finditer(text):
        author = match.group(1).strip()
        year = match.group(2)
        citations.append({
            "type": "author_year",
            "author": author,
            "year": year,
            "raw": f"{author} ({year})",
        })
    return citations
def extract_numbered_refs(text):
    """Extract numbered reference list entries like [1] Author. Title..."""
    citations = []
    for match in PATTERNS["numbered_ref"].finditer(text):
        num = match.group(1)
        content = match.group(2).strip()
        citations.append({
            "type": "numbered",
            "number": int(num),
            "content": content,
            "raw": f"[{num}] {content}",
        })
    return citations
def deduplicate(citations):
    """Remove duplicate citations based on raw text."""
    seen = OrderedDict()
    for c in citations:
        key = c.get("doi") or c.get("url") or c.get("raw", "")
        key = key.lower().strip()
        if key and key not in seen:
            seen[key] = c
    return list(seen.values())
def classify_source(citation):
    """Classify citation as primary, secondary, or tertiary."""
    raw = citation.get("content", citation.get("raw", "")).lower()
    if any(kw in raw for kw in ["meta-analysis", "systematic review", "literature review", "survey of"]):
        return "secondary"
    if any(kw in raw for kw in ["textbook", "encyclopedia", "handbook", "dictionary"]):
        return "tertiary"
    return "primary"
def format_apa(citation):
    """Format citation in APA 7 style."""
    if citation["type"] == "doi":
        return f"https://doi.org/{citation['doi']}"
    if citation["type"] == "url":
        return f"Retrieved from {citation['url']}"
    if citation["type"] == "author_year":
        return f"{citation['author']} ({citation['year']})."
    if citation["type"] == "numbered":
        return citation["content"]
    return citation.get("raw", "")
def format_ieee(citation):
    """Format citation in IEEE style."""
    if citation["type"] == "doi":
        return f"doi: {citation['doi']}"
    if citation["type"] == "url":
        return f"[Online]. Available: {citation['url']}"
    if citation["type"] == "author_year":
        return f"{citation['author']}, {citation['year']}."
    if citation["type"] == "numbered":
        return f"[{citation['number']}] {citation['content']}"
    return citation.get("raw", "")
def format_chicago(citation):
    """Format citation in Chicago style."""
    if citation["type"] == "doi":
        return f"https://doi.org/{citation['doi']}."
    if citation["type"] == "url":
        return f"{citation['url']}."
    if citation["type"] == "author_year":
        return f"{citation['author']}. {citation['year']}."
    if citation["type"] == "numbered":
        return citation["content"]
    return citation.get("raw", "")
def format_harvard(citation):
    """Format citation in Harvard style."""
    if citation["type"] == "doi":
        return f"doi:{citation['doi']}"
    if citation["type"] == "url":
        return f"Available at: {citation['url']}"
    if citation["type"] == "author_year":
        return f"{citation['author']} ({citation['year']})"
    if citation["type"] == "numbered":
        return citation["content"]
    return citation.get("raw", "")

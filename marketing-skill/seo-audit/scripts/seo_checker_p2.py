# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_checker_base import *  # noqa: F403,E402
# fmt: off
from seo_checker_p1 import SEOParser, _is_external  # noqa: E402,E501
# fmt: on


def analyze_html(html: str, base_domain: str = "") -> dict:
    parser = SEOParser()
    parser.feed(html)

    results = {}

    # --- Title ---
    title = parser.title.strip()
    title_len = len(title)
    title_ok = 50 <= title_len <= 60
    results["title"] = {
        "value": title,
        "length": title_len,
        "optimal_range": "50-60 chars",
        "pass": title_ok,
        "score": 100 if title_ok else (50 if title else 0),
        "note": "Good length" if title_ok else (
            f"Too {'short' if title_len < 50 else 'long'} ({title_len} chars)" if title else "Missing title tag"
        ),
    }

    # --- Meta description ---
    desc = parser.meta_description.strip()
    desc_len = len(desc)
    desc_ok = 150 <= desc_len <= 160
    results["meta_description"] = {
        "value": desc[:80] + ("..." if len(desc) > 80 else ""),
        "length": desc_len,
        "optimal_range": "150-160 chars",
        "pass": desc_ok,
        "score": 100 if desc_ok else (50 if 100 <= desc_len < 150 or 160 < desc_len <= 200 else (30 if desc else 0)),
        "note": "Good length" if desc_ok else (
            f"Too {'short' if desc_len < 150 else 'long'} ({desc_len} chars)" if desc else "Missing meta description"
        ),
    }

    # --- H1 ---
    h1s = [t for lvl, t in parser.h_tags if lvl == 1]
    h1_count = len(h1s)
    h1_ok = h1_count == 1
    results["h1"] = {
        "count": h1_count,
        "values": h1s,
        "pass": h1_ok,
        "score": 100 if h1_ok else (50 if h1_count > 1 else 0),
        "note": "Exactly one H1 ✓" if h1_ok else (
            f"Multiple H1s ({h1_count})" if h1_count > 1 else "No H1 found"
        ),
    }

    # --- Heading hierarchy ---
    heading_issues = []
    prev_level = 0
    for lvl, _ in parser.h_tags:
        if prev_level and lvl > prev_level + 1:
            heading_issues.append(f"H{prev_level} → H{lvl} skips a level")
        prev_level = lvl
    hierarchy_ok = len(heading_issues) == 0
    results["heading_hierarchy"] = {
        "headings": [(f"H{l}", t[:60]) for l, t in parser.h_tags],
        "issues": heading_issues,
        "pass": hierarchy_ok,
        "score": max(0, 100 - len(heading_issues) * 25),
        "note": "Hierarchy OK" if hierarchy_ok else f"{len(heading_issues)} level-skip issue(s)",
    }

    # --- Image alt text ---
    total_imgs = len(parser.images)
    imgs_with_alt = sum(1 for img in parser.images if img["alt"] is not None and img["alt"].strip())
    alt_pct = (imgs_with_alt / total_imgs * 100) if total_imgs else 100
    alt_ok = alt_pct == 100
    results["image_alt_text"] = {
        "total_images": total_imgs,
        "with_alt": imgs_with_alt,
        "coverage_pct": round(alt_pct, 1),
        "pass": alt_ok,
        "score": round(alt_pct),
        "note": "All images have alt text" if alt_ok else f"{total_imgs - imgs_with_alt} image(s) missing alt",
    }

    # --- Link ratio ---
    total_links = len(parser.links)
    ext_links = sum(1 for l in parser.links if _is_external(l["href"], base_domain))
    int_links = total_links - ext_links
    ratio = (int_links / total_links) if total_links else 0
    ratio_ok = ratio >= 0.5 or total_links == 0
    results["link_ratio"] = {
        "total_links": total_links,
        "internal": int_links,
        "external": ext_links,
        "internal_pct": round(ratio * 100, 1),
        "pass": ratio_ok,
        "score": 100 if ratio_ok else round(ratio * 100),
        "note": "Good internal/external balance" if ratio_ok else "More external than internal links",
    }

    # --- Word count ---
    body_text = " ".join(parser.body_text_parts)
    words = re.findall(r"\b\w+\b", body_text)
    word_count = len(words)
    wc_ok = word_count >= 300
    results["word_count"] = {
        "count": word_count,
        "minimum": 300,
        "pass": wc_ok,
        "score": min(100, round(word_count / 300 * 100)) if not wc_ok else 100,
        "note": f"{word_count} words (good)" if wc_ok else f"Only {word_count} words — need 300+",
    }

    # --- Viewport meta ---
    results["viewport_meta"] = {
        "present": parser.viewport_meta,
        "pass": parser.viewport_meta,
        "score": 100 if parser.viewport_meta else 0,
        "note": "Mobile viewport tag present" if parser.viewport_meta else "Missing viewport meta tag",
    }

    return results

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_scorer_base import *  # noqa: F403,E402


def score_seo(text: str, title: str = "", keyword: str = "") -> dict:
    """Score SEO signals 0-25 (25% of total)."""
    text_lower = text.lower()
    title_lower = title.lower()
    keyword_lower = keyword.lower()

    points = 0
    signals = {}

    # Title contains keyword
    if keyword_lower and keyword_lower in title_lower:
        points += 7
        signals["keyword_in_title"] = True
    else:
        signals["keyword_in_title"] = False

    # Keyword in first 100 words
    first_100 = " ".join(re.findall(r'\b\w+\b', text_lower)[:100])
    if keyword_lower and keyword_lower in first_100:
        points += 5
        signals["keyword_in_intro"] = True
    else:
        signals["keyword_in_intro"] = False

    # Keyword density (target 0.5-2%)
    words = re.findall(r'\b\w+\b', text_lower)
    n_words = max(1, len(words))
    kw_words = keyword_lower.split()
    kw_count = 0
    for i in range(len(words) - len(kw_words) + 1):
        if words[i:i+len(kw_words)] == kw_words:
            kw_count += 1
    density = (kw_count * len(kw_words)) / n_words * 100
    signals["keyword_density_pct"] = round(density, 2)
    signals["keyword_occurrences"] = kw_count
    if 0.5 <= density <= 2.5:
        points += 5
    elif kw_count > 0:
        points += 2

    # H2 headings present
    h2_count = len(re.findall(r'^## .+', text, re.MULTILINE))
    signals["h2_count"] = h2_count
    if h2_count >= 3:
        points += 5
    elif h2_count >= 1:
        points += 2

    # Title length
    signals["title_length"] = len(title)
    if 30 <= len(title) <= 65:
        points += 3

    total = min(25, points)
    return {"score": total, "max": 25, **signals}
def score_structure(text: str) -> dict:
    """Score structure 0-25 (25% of total)."""
    points = 0
    signals = {}

    lines = text.strip().split('\n')

    # Intro: first non-empty paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    signals["paragraph_count"] = len(paragraphs)

    # Has intro (first paragraph isn't a heading)
    if paragraphs and not paragraphs[0].startswith('#'):
        intro_words = len(paragraphs[0].split())
        signals["intro_word_count"] = intro_words
        if 30 <= intro_words <= 200:
            points += 7
        elif intro_words > 0:
            points += 3
    else:
        signals["intro_word_count"] = 0

    # Has H2 sections
    h2s = [l for l in lines if l.startswith('## ')]
    signals["h2_count"] = len(h2s)
    if len(h2s) >= 4:
        points += 8
    elif len(h2s) >= 2:
        points += 5
    elif len(h2s) >= 1:
        points += 2

    # Has conclusion (last substantial paragraph)
    last_para = paragraphs[-1] if paragraphs else ""
    conclusion_words = len(last_para.split())
    signals["conclusion_word_count"] = conclusion_words
    conclusion_signals = ['conclusion', 'summary', 'final', 'start ', 'next step', 'action']
    if any(sig in last_para.lower() for sig in conclusion_signals) and conclusion_words >= 20:
        points += 7
    elif conclusion_words >= 30:
        points += 4

    # Average paragraph length (web = shorter is better)
    para_lengths = [len(p.split()) for p in paragraphs if not p.startswith('#')]
    if para_lengths:
        avg_para_len = sum(para_lengths) / len(para_lengths)
        signals["avg_paragraph_word_count"] = round(avg_para_len, 1)
        if avg_para_len <= 80:
            points += 3
    else:
        signals["avg_paragraph_word_count"] = 0

    total = min(25, points)
    return {"score": total, "max": 25, **signals}

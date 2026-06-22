# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from humanizer_scorer_base import *  # noqa: F403,E402
# fmt: off
from humanizer_scorer_p1 import HEDGING_PHRASES, PASSIVE_PATTERNS, VAGUE_AUTHORITY  # noqa: E402,E501
# fmt: on


def score_sentence_variance(text: str) -> dict:
    """Score 0-20: high variance = more human (robots use uniform length)."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.split()) >= 3]

    if len(sentences) < 3:
        return {"score": 10, "max": 20, "std_dev": 0, "avg_length": 0, "note": "too few sentences to score"}

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    # Good human writing has std_dev of 8-15 for mixed content
    if std_dev >= 12:
        score = 20
    elif std_dev >= 8:
        score = 16
    elif std_dev >= 5:
        score = 10
    elif std_dev >= 3:
        score = 5
    else:
        score = 0  # very robotic: all sentences same length

    return {
        "score": score,
        "max": 20,
        "std_dev": round(std_dev, 1),
        "avg_length": round(avg, 1),
        "min_length": min(lengths),
        "max_length": max(lengths),
    }
def score_passive_voice(text: str) -> dict:
    """Score 0-20: less passive = more human."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    n_sentences = max(1, len(sentences))

    passive_count = 0
    for pattern in PASSIVE_PATTERNS:
        passive_count += len(re.findall(pattern, text, re.IGNORECASE))

    passive_ratio = passive_count / n_sentences

    if passive_ratio < 0.1:
        score = 20
    elif passive_ratio < 0.2:
        score = 16
    elif passive_ratio < 0.3:
        score = 10
    elif passive_ratio < 0.4:
        score = 5
    else:
        score = 0

    return {
        "score": score,
        "max": 20,
        "passive_count": passive_count,
        "passive_ratio": round(passive_ratio, 2),
        "passive_pct": f"{round(passive_ratio * 100)}%",
    }
def score_hedging(text: str) -> dict:
    """Score 0-15: fewer hedges = more direct = more human."""
    text_lower = text.lower()
    hits = []
    for phrase in HEDGING_PHRASES:
        count = text_lower.count(phrase)
        if count > 0:
            hits.append((phrase, count))

    total_hedges = sum(c for _, c in hits)

    if total_hedges == 0:
        score = 15
    elif total_hedges == 1:
        score = 12
    elif total_hedges == 2:
        score = 8
    elif total_hedges == 3:
        score = 4
    else:
        score = 0

    vague_hits = sum(text_lower.count(p) for p in VAGUE_AUTHORITY)

    return {
        "score": score,
        "max": 15,
        "hedge_count": total_hedges,
        "vague_authority_count": vague_hits,
        "flagged_phrases": [f for f, _ in hits],
    }
def score_em_dashes(text: str) -> dict:
    """Score 0-10: moderate em-dash use is fine; overuse is a tell."""
    # Count em-dashes (—) and double-hyphen (--) used as em-dash
    em_count = text.count('—') + text.count('--')
    word_count = max(1, len(re.findall(r'\b\w+\b', text)))
    per_100 = em_count / (word_count / 100)

    if per_100 < 0.5:
        score = 10  # none or very rare: fine
    elif per_100 < 1.5:
        score = 8   # occasional: good
    elif per_100 < 3:
        score = 5   # frequent: suspicious
    elif per_100 < 5:
        score = 2   # overuse: likely AI
    else:
        score = 0   # compulsive: AI fingerprint

    return {
        "score": score,
        "max": 10,
        "em_dash_count": em_count,
        "per_100_words": round(per_100, 2),
    }

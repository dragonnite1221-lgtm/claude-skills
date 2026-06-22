# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from humanizer_scorer_base import *  # noqa: F403,E402
# fmt: off
from humanizer_scorer_p1 import score_ai_vocabulary  # noqa: E402,E501
from humanizer_scorer_p2 import score_em_dashes, score_hedging, score_passive_voice, score_sentence_variance  # noqa: E402,E501
# fmt: on


def score_paragraph_variety(text: str) -> dict:
    """Score 0-10: varied paragraph lengths = more human."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
    if len(paragraphs) < 3:
        return {"score": 5, "max": 10, "note": "too few paragraphs to score"}

    lengths = [len(p.split()) for p in paragraphs]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    # Has any single-sentence paragraphs? (hallmark of human writing)
    has_short = any(l <= 15 for l in lengths)
    has_long = any(l >= 80 for l in lengths)

    score = 0
    if std_dev >= 30:
        score += 5
    elif std_dev >= 15:
        score += 3
    elif std_dev >= 5:
        score += 1

    if has_short:
        score += 3
    if has_long and std_dev >= 15:
        score += 2

    score = min(10, score)
    return {
        "score": score,
        "max": 10,
        "paragraph_count": len(paragraphs),
        "paragraph_std_dev": round(std_dev, 1),
        "has_short_paragraphs": has_short,
        "avg_paragraph_words": round(avg, 1),
    }
def score_humanity(text: str) -> dict:
    vocab = score_ai_vocabulary(text)
    variance = score_sentence_variance(text)
    passive = score_passive_voice(text)
    hedging = score_hedging(text)
    em = score_em_dashes(text)
    paragraphs = score_paragraph_variety(text)

    total = vocab["score"] + variance["score"] + passive["score"] + hedging["score"] + em["score"] + paragraphs["score"]

    if total >= 85:
        label = "Sounds human ✅"
    elif total >= 70:
        label = "Mostly human — light edits needed"
    elif total >= 50:
        label = "Mixed — AI patterns detectable"
    elif total >= 30:
        label = "Robotic — significant rewrite needed"
    else:
        label = "AI fingerprint — full rewrite required 🔴"

    return {
        "humanity_score": total,
        "label": label,
        "sections": {
            "ai_vocabulary": vocab,
            "sentence_variance": variance,
            "passive_voice": passive,
            "hedging": hedging,
            "em_dashes": em,
            "paragraph_variety": paragraphs,
        }
    }

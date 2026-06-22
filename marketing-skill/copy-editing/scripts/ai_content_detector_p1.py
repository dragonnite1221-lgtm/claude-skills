# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_content_detector_base import *  # noqa: F403,E402


AI_PHRASES = [
    "in today's digital landscape",
    "in today's fast-paced",
    "it's worth noting that",
    "it is important to note",
    "delve into",
    "dive deep into",
    "leverage",
    "game-changer",
    "game changer",
    "unlock the potential",
    "unlock the power",
    "harness the power",
    "at the end of the day",
    "in conclusion",
    "in summary",
    "navigating the complexities",
    "a comprehensive guide",
    "seamlessly integrate",
    "robust solution",
    "cutting-edge",
    "state-of-the-art",
    "empower you to",
    "take your .* to the next level",
    "in the realm of",
    "tapestry of",
    "multifaceted",
    "it's crucial to",
    "paramount",
    "foster a .* environment",
    "elevate your",
]
AI_PHRASE_RES = [re.compile(p, re.IGNORECASE) for p in AI_PHRASES]
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+", re.DOTALL)
WORD_RE = re.compile(r"[a-zA-Z]+")
DEMO_CONTENT = """In today's digital landscape, leveraging AI tools has become a game-changer for content creators. It's worth noting that the ability to harness the power of large language models can unlock the potential of your marketing efforts. This comprehensive guide will delve into the multifaceted world of AI-assisted content creation.

The integration of AI into content workflows is a robust solution that seamlessly integrates with existing processes. By navigating the complexities of modern content production, you can elevate your brand's voice and foster a creative environment that empowers your team to take their content to the next level.

At the end of the day, it's crucial to understand that AI is a tool, not a replacement. The cutting-edge capabilities of state-of-the-art models are paramount for staying competitive in the realm of digital marketing. In conclusion, the tapestry of modern content creation requires both human creativity and artificial intelligence working in harmony."""
def extract_sentences(text):
    body = re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL)
    body = re.sub(r"^#+\s+.*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"`[^`]+`", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    sentences = SENTENCE_RE.findall(body)
    return [s.strip() for s in sentences if len(s.strip().split()) >= 3]
def burstiness_score(sentences):
    """Compute burstiness (sentence length variance). High = human, low = AI."""
    if len(sentences) < 5:
        return {"score": 50, "mean": 0, "std": 0, "cv": 0, "note": "too few sentences"}
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    cv = std / mean if mean > 0 else 0  # coefficient of variation

    # Human writing: CV typically 0.4-0.8+ (high variance)
    # AI writing: CV typically 0.15-0.35 (consistently medium)
    if cv >= 0.5:
        ai_prob = max(0, 30 - (cv - 0.5) * 60)
    elif cv >= 0.35:
        ai_prob = 30 + (0.5 - cv) * 130
    else:
        ai_prob = 50 + (0.35 - cv) * 250

    ai_prob = max(0, min(100, ai_prob))
    return {
        "score": round(ai_prob, 1),
        "mean_sentence_length": round(mean, 1),
        "std_sentence_length": round(std, 1),
        "coefficient_of_variation": round(cv, 3),
        "note": "low CV = flat sentence lengths (AI-like)" if cv < 0.35 else "healthy variance",
    }
def vocabulary_diversity(text):
    """Type-Token Ratio. Low TTR = repetitive vocabulary (AI-like)."""
    body = re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL)
    words = [w.lower() for w in WORD_RE.findall(body) if len(w) > 2]
    if len(words) < 50:
        return {"score": 50, "ttr": 0, "unique": 0, "total": len(words), "note": "too few words"}
    # Use a sliding window TTR for length-independence
    window = min(200, len(words))
    ttrs = []
    for i in range(0, len(words) - window + 1, window // 2):
        chunk = words[i : i + window]
        ttrs.append(len(set(chunk)) / len(chunk))
    avg_ttr = sum(ttrs) / len(ttrs)

    # Human: TTR 0.55-0.75+ (varied vocabulary)
    # AI: TTR 0.35-0.50 (repetitive patterns)
    if avg_ttr >= 0.60:
        ai_prob = max(0, 25 - (avg_ttr - 0.60) * 150)
    elif avg_ttr >= 0.45:
        ai_prob = 25 + (0.60 - avg_ttr) * 330
    else:
        ai_prob = 75 + (0.45 - avg_ttr) * 250

    ai_prob = max(0, min(100, ai_prob))

    # Top repeated words (excluding stop words)
    stop = {"the", "and", "for", "that", "this", "with", "from", "are", "was", "were", "been",
            "have", "has", "had", "not", "but", "can", "will", "your", "you", "they", "their",
            "more", "than", "also", "into", "when", "how", "what", "which", "about", "each"}
    content_words = [w for w in words if w not in stop]
    top_repeated = Counter(content_words).most_common(5)

    return {
        "score": round(ai_prob, 1),
        "avg_ttr": round(avg_ttr, 3),
        "unique_words": len(set(words)),
        "total_words": len(words),
        "top_repeated": [{"word": w, "count": c} for w, c in top_repeated],
        "note": "low TTR = repetitive vocabulary (AI-like)" if avg_ttr < 0.45 else "healthy diversity",
    }

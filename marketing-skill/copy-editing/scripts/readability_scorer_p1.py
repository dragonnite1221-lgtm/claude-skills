# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from readability_scorer_base import *  # noqa: F403,E402


FILLER_WORDS = [
    "very", "really", "just", "actually", "basically", "literally",
    "honestly", "totally", "absolutely", "definitely", "certainly",
    "obviously", "clearly", "quite", "rather", "somewhat", "fairly",
    "pretty", "simply", "truly", "genuinely", "essentially",
]
PASSIVE_PATTERN = re.compile(
    r"\b(was|were|is|are|been|being|be|am)\s+(\w+ed|known|written|built|made|done|seen|given|taken|brought|thought|found|put|set|cut|read|let|hit|hurt|cost|led|felt|kept|left|meant|sent|spent|stood|told|wore|won|beat|lost|broke|chose|drove|flew|froze|grew|hid|rang|rode|rose|ran|sank|sang|spoke|swore|swam|threw|woke|wrote)\b",
    re.IGNORECASE,
)
ADVERB_PATTERN = re.compile(r"\b\w+ly\b", re.IGNORECASE)
def count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:\"'")
    if not word:
        return 0
    # Silent e
    if word.endswith("e") and len(word) > 2:
        word = word[:-1]
    count = len(re.findall(r"[aeiou]+", word))
    return max(1, count)
def split_sentences(text: str) -> list:
    # Split on sentence-ending punctuation
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]
def split_words(text: str) -> list:
    return re.findall(r"\b[a-zA-Z]+\b", text)
def flesch_reading_ease(avg_sentence_len: float, avg_syllables: float) -> float:
    """Flesch Reading Ease formula."""
    score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables)
    return round(max(0.0, min(100.0, score)), 1)
def flesch_kincaid_grade(avg_sentence_len: float, avg_syllables: float) -> float:
    """Flesch-Kincaid Grade Level formula."""
    grade = (0.39 * avg_sentence_len) + (11.8 * avg_syllables) - 15.59
    return round(max(0.0, grade), 1)
def ease_label(score: float) -> str:
    if score >= 90: return "Very Easy (5th grade)"
    if score >= 80: return "Easy (6th grade)"
    if score >= 70: return "Fairly Easy (7th grade)"
    if score >= 60: return "Standard (8-9th grade)"
    if score >= 50: return "Fairly Difficult (10-12th grade)"
    if score >= 30: return "Difficult (College)"
    return "Very Confusing (Professional)"
def analyze_text(text: str) -> dict:
    sentences = split_sentences(text)
    words = split_words(text)

    if not words:
        return {"error": "No readable text found."}

    num_sentences = max(1, len(sentences))
    num_words = len(words)

    # Syllables
    syllable_counts = [count_syllables(w) for w in words]
    total_syllables = sum(syllable_counts)

    avg_sentence_len = num_words / num_sentences
    avg_word_len = sum(len(w) for w in words) / num_words
    avg_syllables_per_word = total_syllables / num_words

    fre = flesch_reading_ease(avg_sentence_len, avg_syllables_per_word)
    fk_grade = flesch_kincaid_grade(avg_sentence_len, avg_syllables_per_word)

    # Passive voice
    passive_matches = PASSIVE_PATTERN.findall(text)
    passive_count = len(passive_matches)
    passive_pct = round(passive_count / num_sentences * 100, 1)

    # Adverbs
    adverb_matches = ADVERB_PATTERN.findall(text)
    # Filter obvious non-adverbs
    non_adverb = {"family", "early", "only", "likely", "nearly", "really",
                  "daily", "weekly", "monthly", "yearly", "friendly", "lovely",
                  "lonely", "lively", "elderly", "costly"}
    adverbs = [a for a in adverb_matches if a.lower() not in non_adverb]
    adverb_density = round(len(adverbs) / num_words * 100, 1)

    # Filler words
    text_lower = text.lower()
    word_tokens_lower = [w.lower() for w in words]
    filler_found = {fw: word_tokens_lower.count(fw) for fw in FILLER_WORDS if fw in word_tokens_lower}
    filler_total = sum(filler_found.values())

    # Scoring:
    # FRE already 0-100 (higher = easier = better for marketing copy)
    # Target for marketing: 60-80 range
    fre_score = fre  # use as-is

    return {
        "stats": {
            "word_count": num_words,
            "sentence_count": num_sentences,
            "avg_sentence_length": round(avg_sentence_len, 1),
            "avg_word_length": round(avg_word_len, 1),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        },
        "flesch_reading_ease": {
            "score": fre,
            "label": ease_label(fre),
            "target": "60-80 for most marketing copy",
        },
        "flesch_kincaid_grade": {
            "grade_level": fk_grade,
            "note": f"Equivalent to grade {fk_grade} reading level",
        },
        "passive_voice": {
            "count": passive_count,
            "percentage": passive_pct,
            "target": "<10%",
            "pass": passive_pct < 10,
        },
        "adverb_density": {
            "count": len(adverbs),
            "percentage": adverb_density,
            "examples": list(set(adverbs))[:8],
            "target": "<5%",
            "pass": adverb_density < 5,
        },
        "filler_words": {
            "total_count": filler_total,
            "breakdown": filler_found,
            "target": "0-3 per 100 words",
            "per_100_words": round(filler_total / num_words * 100, 1),
        },
        "overall_score": round(fre),
    }

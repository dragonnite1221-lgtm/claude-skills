# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from email_sequence_analyzer_base import *  # noqa: F403,E402


SPAM_TRIGGERS = [
    "free", "guaranteed", "no obligation", "act now", "limited time",
    "click here", "earn money", "make money", "risk-free", "special offer",
    "no cost", "winner", "congratulations", "you've been selected",
    "once in a lifetime", "urgent", "don't miss out", "buy now",
    "order now", "100%", "best price", "lowest price", "incredible deal",
    "amazing offer", "cash bonus", "extra cash", "fast cash",
    "you have been chosen", "exclusive deal", "as seen on",
    "dear friend", "valued customer",
]
PERSONALIZATION_SIGNALS = [
    # Direct references to "you"
    r'\byou(?:r|rs|\'re|\'ve|\'d|\'ll)?\b',
    # Trigger references
    r'\b(?:saw|noticed|read|heard|saw|found|noted)\b',
    # Named observation patterns
    r'\b(?:your team|your company|your role|your work|your recent|your post)\b',
    # Industry/role-specific references
    r'\b(?:as a|in your|at your|given your)\b',
    # Specific numbers or facts
    r'\b\d{4}\b',  # years — often a sign of specific research
    r'\$\d+|\d+%',  # numbers with $ or %
]
DEAD_OPENERS = [
    "i hope this email finds you well",
    "i hope this finds you",
    "i wanted to reach out",
    "i am reaching out",
    "my name is",
    "i'm writing to",
    "i am writing to",
    "hope you're doing well",
    "i hope you are doing well",
    "just following up",
    "just checking in",
    "circling back",
    "touching base",
    "per my last email",
    "as per my previous",
]
WEAK_CTA = [
    "let me know if you're interested",
    "let me know if you would be interested",
    "feel free to",
    "please don't hesitate",
    "if you have any questions",
    "looking forward to hearing from you",
    "i look forward to connecting",
    "hope we can connect",
]
STRONG_CTA_PATTERNS = [
    r'\b(?:15|20|30|45|60)[\s-]?minute\b',   # time-specific meeting ask
    r'\b(?:call|chat|talk|speak|connect|meet)\b.*\?',  # question + meeting word
    r'worth\s+(?:a|an)\b',                   # "worth a call?"
    r'\?$',                                   # ends with question
    r'\buseful\b\s*\?',                       # "useful?"
    r'\b(?:reply|respond)\b',                 # explicit reply ask
]
def count_words(text: str) -> int:
    return len(text.split())
def count_sentences(text: str) -> int:
    """Rough sentence count by terminal punctuation."""
    sentences = re.split(r'[.!?]+', text)
    return max(1, len([s for s in sentences if s.strip()]))
def avg_words_per_sentence(text: str) -> float:
    words = count_words(text)
    sentences = count_sentences(text)
    return words / sentences if sentences else words
def avg_chars_per_word(text: str) -> float:
    words = text.split()
    if not words:
        return 0
    return sum(len(w.strip('.,!?;:')) for w in words) / len(words)
def flesch_reading_ease(text: str) -> float:
    """
    Approximate Flesch Reading Ease score.
    206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    We approximate syllables as: max(1, len(word) * 0.4) for each word.
    """
    words = text.split()
    if not words:
        return 0
    sentences = count_sentences(text)
    syllables = sum(max(1, int(len(re.sub(r'[^aeiouAEIOU]', '', w)) * 1.2) or 1) for w in words)
    asl = len(words) / sentences  # avg sentence length
    asw = syllables / len(words)  # avg syllables per word
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return max(0, min(100, score))
def grade_reading_level(fre_score: float) -> str:
    """Convert Flesch Reading Ease to a human label."""
    if fre_score >= 70:
        return "Easy (conversational)"
    if fre_score >= 60:
        return "Plain English"
    if fre_score >= 50:
        return "Fairly difficult"
    return "Difficult (too complex for cold email)"

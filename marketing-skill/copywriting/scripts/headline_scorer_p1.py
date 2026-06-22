# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from headline_scorer_base import *  # noqa: F403,E402


POWER_WORDS = {
    # urgency / scarcity
    "now", "today", "instantly", "immediately", "urgent", "limited",
    "exclusive", "last", "hurry", "deadline", "expires", "fast",
    # value / benefit
    "free", "save", "proven", "guaranteed", "results", "boost",
    "increase", "grow", "maximize", "unlock", "secret", "revealed",
    "transform", "master", "ultimate", "best", "top", "powerful",
    # curiosity / intrigue
    "discover", "uncover", "surprising", "shocking", "hidden",
    "unknown", "insider", "hack", "trick", "truth",
    # social proof / authority
    "experts", "researchers", "scientists", "officially", "certified",
    "award-winning", "world-class",
    # ease / simplicity
    "easy", "simple", "effortless", "quick", "step-by-step",
    "foolproof", "beginner", "without",
    # negative triggers (fear/loss)
    "avoid", "stop", "never", "mistake", "fail", "warning", "danger",
    "worst", "deadly", "risky",
}
EMOTIONAL_TRIGGERS = {
    "love", "hate", "fear", "hope", "joy", "pain", "anger", "envy",
    "trust", "doubt", "regret", "pride", "shame", "relief", "success",
    "failure", "happiness", "frustration", "excitement", "anxiety",
    "lonely", "powerful", "confident", "inspired",
}
JARGON_WORDS = {
    "synergy", "leverage", "disruptive", "paradigm", "scalable",
    "bandwidth", "circle back", "ping", "holistic", "ecosystem",
    "utilize", "facilitate", "ideate", "incentivize", "stakeholders",
    "deliverables", "actionable", "bespoke", "granular", "boil the ocean",
    "low-hanging fruit", "move the needle", "thought leader", "deep dive",
}
def tokenize(headline: str) -> list:
    return re.findall(r"\b\w+(?:[-']\w+)*\b", headline.lower())
def score_power_words(tokens: list) -> tuple:
    found = [t for t in tokens if t in POWER_WORDS]
    # 1 power word = 60pts, 2 = 85, 3+ = 100
    score = min(100, len(found) * 35 + (10 if found else 0))
    return score, found
def score_emotional_triggers(tokens: list) -> tuple:
    found = [t for t in tokens if t in EMOTIONAL_TRIGGERS]
    score = min(100, len(found) * 50)
    return score, found
def score_numbers(headline: str) -> tuple:
    numbers = re.findall(r"\b\d+(?:[,\.]\d+)?%?\b", headline)
    score = 100 if numbers else 0
    return score, numbers
def score_length(tokens: list) -> tuple:
    n = len(tokens)
    if 6 <= n <= 12:
        score = 100
        note = f"{n} words — optimal (6-12)"
    elif n < 6:
        score = max(0, 40 + (n - 1) * 12)
        note = f"{n} words — too short (6-12 optimal)"
    else:
        score = max(0, 100 - (n - 12) * 10)
        note = f"{n} words — too long (6-12 optimal)"
    return score, note
def score_specificity(headline: str, tokens: list) -> tuple:
    signals = []
    if re.search(r"\b\d+\b", headline):
        signals.append("contains number")
    if re.search(r"\b(in \d+|within \d+|\d+ days?|\d+ weeks?|\d+ months?|\d+ hours?|\d+ minutes?)\b", headline, re.I):
        signals.append("timeframe")
    if re.search(r"\b(how to|step|guide|checklist|strategy|system|framework|formula)\b", headline, re.I):
        signals.append("concrete format")
    if re.search(r"\b\d+%\b", headline):
        signals.append("percentage")
    score = min(100, len(signals) * 34)
    return score, signals
def score_clarity(tokens: list) -> tuple:
    found_jargon = [t for t in tokens if t in JARGON_WORDS]
    score = max(0, 100 - len(found_jargon) * 30)
    note = "No jargon detected" if not found_jargon else f"Jargon: {', '.join(found_jargon)}"
    return score, note
WEIGHTS = {
    "power_words":        0.25,
    "emotional_triggers": 0.15,
    "numbers":            0.15,
    "length":             0.20,
    "specificity":        0.15,
    "clarity":            0.10,
}
def score_headline(headline: str) -> dict:
    tokens = tokenize(headline)

    pw_score, pw_found = score_power_words(tokens)
    et_score, et_found = score_emotional_triggers(tokens)
    num_score, nums = score_numbers(headline)
    len_score, len_note = score_length(tokens)
    spec_score, spec_signals = score_specificity(headline, tokens)
    clar_score, clar_note = score_clarity(tokens)

    breakdown = {
        "power_words":        {"score": pw_score,   "found": pw_found,      "weight": "25%"},
        "emotional_triggers": {"score": et_score,   "found": et_found,      "weight": "15%"},
        "numbers":            {"score": num_score,  "found": nums,           "weight": "15%"},
        "length":             {"score": len_score,  "note": len_note,        "weight": "20%"},
        "specificity":        {"score": spec_score, "signals": spec_signals, "weight": "15%"},
        "clarity":            {"score": clar_score, "note": clar_note,       "weight": "10%"},
    }

    overall = round(sum(
        breakdown[k]["score"] * WEIGHTS[k]
        for k in WEIGHTS
    ))

    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"

    return {
        "headline": headline,
        "overall_score": overall,
        "grade": grade,
        "breakdown": breakdown,
    }
DEMO_HEADLINES = [
    "10 Proven Ways to Double Your Email Open Rates in 30 Days",
    "Marketing Tips for Better Results",
    "Unlock the Secret Formula That Top Experts Use to Grow Revenue Fast",
    "How to Leverage Synergistic Paradigms for Scalable Growth",
    "Our New Product Is Now Available",
]

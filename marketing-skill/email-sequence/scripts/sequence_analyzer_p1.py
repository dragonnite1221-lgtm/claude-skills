# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sequence_analyzer_base import *  # noqa: F403,E402


SPAM_TRIGGER_WORDS = [
    "free", "guarantee", "guaranteed", "winner", "won", "prize",
    "congratulations", "cash", "earn money", "make money", "extra income",
    "100% free", "no cost", "risk free", "act now", "limited time",
    "click here", "buy now", "order now", "get it now",
    "as seen on", "dear friend", "you have been selected",
    "this isn't spam", "not spam", "no credit card required",
    "special promotion", "special offer", "amazing offer",
    "!!!", "!!!", "$$$", "£££",
    "increase your", "increase sales", "double your",
    "lose weight", "weight loss", "diet", "viagra", "casino",
]
CTA_PATTERNS = re.compile(
    r"\b(click|tap|reply|download|sign up|register|buy|purchase|get started|"
    r"learn more|read more|visit|go to|check out|schedule|book|claim|try|"
    r"subscribe|join|start|access|watch|see|grab|discover)\b",
    re.IGNORECASE,
)
PERSONALIZATION_TOKENS = re.compile(
    r"\{\{?\s*\w+\s*\}?\}|%\w+%|\[FIRST_NAME\]|\[NAME\]|\[COMPANY\]|\[FIRSTNAME\]",
    re.IGNORECASE,
)
def _body_length_verdict(word_count: int) -> str:
    if word_count < 50:
        return "Too short (<50 words)"
    if word_count <= 150:
        return "Short/punchy — good for re-engagement"
    if word_count <= 300:
        return "Optimal (150-300 words)"
    if word_count <= 500:
        return "Long — ensure high value throughout"
    return "Very long (500+ words) — consider trimming"
def analyze_email(email: dict, index: int) -> dict:
    subject = email.get("subject", "")
    body = email.get("body", "")
    delay = email.get("delay_days", 0)

    # Subject analysis
    subject_len = len(subject)
    subject_word_count = len(subject.split())
    subject_ok = 30 <= subject_len <= 60
    subject_has_number = bool(re.search(r"\d", subject))
    subject_question = subject.strip().endswith("?")
    subject_all_caps = subject == subject.upper() and len(subject) > 3

    # Body analysis
    body_words = re.findall(r"\b\w+\b", body)
    body_word_count = len(body_words)

    # CTA detection
    cta_matches = CTA_PATTERNS.findall(body)
    has_cta = len(cta_matches) > 0

    # Personalization tokens
    tokens_in_subject = PERSONALIZATION_TOKENS.findall(subject)
    tokens_in_body = PERSONALIZATION_TOKENS.findall(body)
    total_tokens = len(tokens_in_subject) + len(tokens_in_body)

    # Spam triggers
    combined = (subject + " " + body).lower()
    spam_found = [w for w in SPAM_TRIGGER_WORDS if w.lower() in combined]

    # Spam score (0-100, higher = more spammy)
    spam_score = min(100, len(spam_found) * 10)

    return {
        "email_index": index + 1,
        "delay_days": delay,
        "subject": {
            "text": subject,
            "length": subject_len,
            "word_count": subject_word_count,
            "length_ok": subject_ok,
            "has_number": subject_has_number,
            "is_question": subject_question,
            "all_caps_warning": subject_all_caps,
            "personalized": len(tokens_in_subject) > 0,
        },
        "body": {
            "word_count": body_word_count,
            "length_verdict": _body_length_verdict(body_word_count),
            "has_cta": has_cta,
            "cta_phrases": list(set(cta_matches))[:5],
            "personalization_tokens": total_tokens,
        },
        "spam": {
            "trigger_words_found": spam_found[:8],
            "trigger_count": len(spam_found),
            "spam_risk_score": spam_score,
            "risk_level": "High" if spam_score >= 40 else "Medium" if spam_score >= 20 else "Low",
        },
    }
def analyze_pacing(emails: list) -> dict:
    if len(emails) <= 1:
        return {"note": "Single email — no pacing to analyze"}

    delays = [e.get("delay_days", 0) for e in emails]
    gaps = [delays[i] - delays[i - 1] for i in range(1, len(delays))]

    issues = []
    for i, gap in enumerate(gaps):
        if gap <= 0:
            issues.append(f"Email {i+2}: same-day or before previous — check delay_days")
        elif gap == 1:
            issues.append(f"Email {i+2}: only 1-day gap — may feel aggressive")
        elif gap > 14:
            issues.append(f"Email {i+2}: {gap}-day gap — momentum may drop")

    # Assess overall cadence
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    if avg_gap <= 2:
        cadence = "Aggressive (avg <2 days)"
    elif avg_gap <= 5:
        cadence = "High-frequency (avg 2-5 days)"
    elif avg_gap <= 10:
        cadence = "Standard (avg 5-10 days)"
    else:
        cadence = "Low-frequency (avg 10+ days)"

    return {
        "email_count": len(emails),
        "total_duration_days": max(delays) - min(delays),
        "avg_gap_days": round(avg_gap, 1),
        "cadence_type": cadence,
        "gaps": gaps,
        "issues": issues,
    }

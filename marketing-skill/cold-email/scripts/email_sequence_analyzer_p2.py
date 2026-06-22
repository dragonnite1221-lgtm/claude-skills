# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from email_sequence_analyzer_base import *  # noqa: F403,E402
# fmt: off
from email_sequence_analyzer_p1 import DEAD_OPENERS, PERSONALIZATION_SIGNALS, SPAM_TRIGGERS, STRONG_CTA_PATTERNS, WEAK_CTA, avg_words_per_sentence, count_words, flesch_reading_ease, grade_reading_level  # noqa: E402,E501
# fmt: on


def analyze_subject_line(subject: str) -> Dict:
    issues = []
    warnings = []

    if not subject:
        return {"length": 0, "issues": ["No subject line provided"], "score": 0}

    length = len(subject)

    if length > 60:
        issues.append(f"Too long ({length} chars) — aim for under 50")
    if length > 50:
        warnings.append("Subject is getting long — shorter subjects get more opens")

    if subject.isupper():
        issues.append("All caps subject lines trigger spam filters")

    if re.search(r'!!!|!{2,}', subject):
        issues.append("Multiple exclamation points look like spam")

    if subject.startswith("Re:") or subject.startswith("Fwd:"):
        lower = subject.lower()
        if lower.startswith("re:") or lower.startswith("fwd:"):
            warnings.append("Fake Re:/Fwd: subjects feel deceptive — people have learned this trick")

    if re.search(r'[A-Z]{4,}', subject) and not subject.isupper():
        warnings.append("SHOUTING words in subject lines look like spam")

    if re.search(r'[\U0001F600-\U0001FFFF]', subject):
        warnings.append("Emojis in subject lines are polarizing and often spam-filtered for B2B")

    if '?' in subject:
        warnings.append("Question mark in subject can feel like an ad — test without")

    # Spam trigger check in subject
    subject_lower = subject.lower()
    triggered = [w for w in SPAM_TRIGGERS if w in subject_lower]
    if triggered:
        issues.append(f"Spam trigger words in subject: {', '.join(triggered)}")

    # Score
    score = 100
    score -= len(issues) * 20
    score -= len(warnings) * 10
    score = max(0, min(100, score))

    return {
        "length": length,
        "issues": issues,
        "warnings": warnings,
        "score": score,
    }
def analyze_body(body: str) -> Dict:
    body_lower = body.lower()
    findings = []
    deductions = []

    word_count = count_words(body)
    fre = flesch_reading_ease(body)
    reading_level = grade_reading_level(fre)
    avg_wps = avg_words_per_sentence(body)

    # Word count scoring
    if word_count > 200:
        deductions.append(("word_count", 15, f"Too long ({word_count} words) — cold emails should be under 150"))
    elif word_count > 150:
        deductions.append(("word_count", 5, f"Getting long ({word_count} words) — aim for under 150"))
    elif word_count < 30:
        deductions.append(("word_count", 10, f"Very short ({word_count} words) — may lack enough context"))

    # Sentence length
    if avg_wps > 25:
        deductions.append(("readability", 10, f"Sentences average {avg_wps:.0f} words — too complex, aim for 15-20"))

    # Dead opener check
    for opener in DEAD_OPENERS:
        if opener in body_lower:
            deductions.append(("opener", 20, f"Dead opener detected: '{opener}' — rewrite the opening"))
            break

    # Personalization density
    pers_matches = 0
    for pattern in PERSONALIZATION_SIGNALS:
        matches = re.findall(pattern, body_lower)
        pers_matches += len(matches)

    pers_density = pers_matches / word_count * 100 if word_count else 0
    if pers_density < 5:
        deductions.append(("personalization", 10, "Low personalization signals — email may feel generic"))

    # Spam trigger words in body
    triggered = [w for w in SPAM_TRIGGERS if w in body_lower]
    if triggered:
        deductions.append(("spam", len(triggered) * 5, f"Spam trigger words: {', '.join(triggered[:5])}"))

    # Weak CTA check
    for weak in WEAK_CTA:
        if weak in body_lower:
            deductions.append(("cta", 10, f"Weak CTA: '{weak}' — be more direct"))
            break

    # Strong CTA check
    has_strong_cta = any(re.search(p, body_lower) for p in STRONG_CTA_PATTERNS)
    if not has_strong_cta:
        deductions.append(("cta", 15, "No clear CTA detected — every cold email needs a single, direct ask"))

    # HTML check
    if re.search(r'<html|<body|<table|<div|style="|font-family:', body_lower):
        deductions.append(("format", 20, "HTML detected — plain text emails get better deliverability for cold outreach"))

    # Multiple links
    links = re.findall(r'https?://', body)
    if len(links) > 2:
        deductions.append(("links", 10, f"{len(links)} links detected — keep to 1-2 max for cold email"))

    # Calculate score
    total_deduction = sum(d[1] for d in deductions)
    score = max(0, min(100, 100 - total_deduction))

    return {
        "word_count": word_count,
        "reading_ease_score": round(fre, 1),
        "reading_level": reading_level,
        "avg_words_per_sentence": round(avg_wps, 1),
        "personalization_density": round(pers_density, 1),
        "has_strong_cta": has_strong_cta,
        "spam_triggers": triggered,
        "deductions": [(d[2], d[1]) for d in deductions],
        "score": score,
    }

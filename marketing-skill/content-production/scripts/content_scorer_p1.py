# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_scorer_base import *  # noqa: F403,E402


SAMPLE_CONTENT = """
Title: How to Reduce Churn in SaaS: 7 Proven Tactics That Actually Work

Introduction

Most SaaS companies discover their churn problem too late — after the customer has already left. By then, the damage is done. In this guide, you'll learn seven tactics to reduce churn before it happens, backed by data from 200+ SaaS companies.

## Why Customers Churn (It's Not What You Think)

Customers don't churn because your product is bad. They churn because they never saw value. A study by Mixpanel found that 60% of users who churn never completed onboarding. That's a product adoption problem, not a satisfaction problem.

Fix the adoption gap first. Everything else is downstream.

## Tactic 1: Instrument Your Activation Funnel

You can't fix what you can't see. Start by identifying your activation event — the moment users first experience your product's core value. For Slack, it's sending 2,000 messages. For Dropbox, it's saving a first file.

Map the funnel from signup to activation. Find where users drop off. That's your highest-leverage intervention point.

## Tactic 2: Segment Your Churn by Cohort

Not all churn is equal. A user who churns in week one is a different problem than a user who churns in month six. Cohort analysis breaks this apart.

Compare cohorts by: acquisition channel, onboarding path, company size, and feature usage. You'll find that certain cohorts churn 3-4x more than others. Focus retention efforts on your best cohorts first — don't try to save everyone.

## Tactic 3: Build a Customer Health Score

A health score is a composite signal that predicts churn before it happens. Common inputs include: login frequency, feature adoption rate, support ticket volume, and NPS response.

Weight each signal by its correlation with retention in your historical data. A score below 40 should trigger a customer success outreach. Don't wait for the cancellation request.

## Conclusion

Churn is a lagging indicator. By the time you see it, the problem happened weeks ago. Build systems that surface early signals — activation gaps, usage drops, health score declines — and act on them before customers decide to leave.

Start with one tactic. Instrument your activation funnel this week.
"""
SAMPLE_KEYWORD = "reduce churn"
SAMPLE_TITLE = "How to Reduce Churn in SaaS: 7 Proven Tactics That Actually Work"
def count_syllables(word: str) -> int:
    """Approximate syllable count using vowel-group heuristic."""
    word = word.lower().strip(".,!?;:")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Adjust for silent e
    if word.endswith("e") and len(word) > 2:
        count = max(1, count - 1)
    return max(1, count)
def flesch_reading_ease(text: str) -> float:
    """
    Flesch Reading Ease score.
    206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    Higher = easier. Target: 60-70 for professional content.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    n_sentences = max(1, len(sentences))

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    n_words = max(1, len(words))

    n_syllables = sum(count_syllables(w) for w in words)

    asl = n_words / n_sentences  # avg sentence length
    asw = n_syllables / n_words  # avg syllables per word

    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(max(0.0, min(100.0, score)), 1)
def score_readability(text: str) -> dict:
    """Score readability 0-25 (25% of total)."""
    fre = flesch_reading_ease(text)

    # FRE → points (target 60-70 for B2B)
    if fre >= 65:
        fre_points = 15
    elif fre >= 55:
        fre_points = 12
    elif fre >= 45:
        fre_points = 8
    elif fre >= 35:
        fre_points = 4
    else:
        fre_points = 0

    # Sentence length variance
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 2]
    lengths = [len(s.split()) for s in sentences]
    if len(lengths) > 1:
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        variance_points = min(10, int(std_dev))  # good variance = high std dev
    else:
        variance_points = 0

    total = min(25, fre_points + variance_points)
    return {
        "score": total,
        "max": 25,
        "flesch_reading_ease": fre,
        "sentence_length_std_dev": round(math.sqrt(variance) if len(lengths) > 1 else 0, 1)
    }

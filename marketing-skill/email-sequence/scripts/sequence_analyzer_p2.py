# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sequence_analyzer_base import *  # noqa: F403,E402


def compute_sequence_score(email_analyses: list, pacing: dict) -> dict:
    if not email_analyses:
        return {"overall": 0}

    # Subject score: avg subject length compliance
    subject_ok_count = sum(1 for e in email_analyses if e["subject"]["length_ok"])
    subject_score = round(subject_ok_count / len(email_analyses) * 100)

    # CTA score: % of emails with CTA
    cta_count = sum(1 for e in email_analyses if e["body"]["has_cta"])
    cta_score = round(cta_count / len(email_analyses) * 100)

    # Personalization score
    personalized_count = sum(1 for e in email_analyses if e["body"]["personalization_tokens"] > 0)
    personalization_score = round(personalized_count / len(email_analyses) * 100)

    # Spam score (inverted — low spam = high score)
    avg_spam = sum(e["spam"]["spam_risk_score"] for e in email_analyses) / len(email_analyses)
    spam_score = max(0, 100 - int(avg_spam))

    # Pacing score
    pacing_issues = len(pacing.get("issues", []))
    pacing_score = max(0, 100 - pacing_issues * 20)

    # Body length score
    length_ok_count = sum(
        1 for e in email_analyses
        if "Optimal" in e["body"]["length_verdict"] or "punchy" in e["body"]["length_verdict"]
    )
    length_score = round(length_ok_count / len(email_analyses) * 100)

    weights = {
        "subject_quality": 0.20,
        "cta_presence":    0.20,
        "spam_safety":     0.25,
        "personalization": 0.15,
        "pacing":          0.10,
        "body_length":     0.10,
    }
    scores = {
        "subject_quality": subject_score,
        "cta_presence":    cta_score,
        "spam_safety":     spam_score,
        "personalization": personalization_score,
        "pacing":          pacing_score,
        "body_length":     length_score,
    }
    overall = round(sum(scores[k] * weights[k] for k in weights))
    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"

    return {
        "overall": overall,
        "grade": grade,
        "breakdown": {k: {"score": v, "weight": f"{int(weights[k]*100)}%"} for k, v in scores.items()},
    }
DEMO_SEQUENCE = [
    {
        "subject": "{{first_name}}, your free marketing audit is ready",
        "body": "Hi {{first_name}},\n\nWe analyzed 500 campaigns like yours and found three quick wins that could double your ROAS in 30 days.\n\nI've put together a custom audit for {{company}}. It's free and takes 10 minutes to review.\n\n→ Click here to see your results: [LINK]\n\nBest,\nSarah",
        "delay_days": 0,
    },
    {
        "subject": "Did you see this, {{first_name}}?",
        "body": "Quick follow-up.\n\nMost marketers we talk to are sitting on 2-3 easy optimizations that could add 20-40% more revenue from the same ad spend.\n\nHere's the #1 thing we see: landing pages that don't match the ad promise.\n\nWorth 5 minutes? → [Review your audit]\n\nSarah",
        "delay_days": 3,
    },
    {
        "subject": "The $50,000 mistake (and how to avoid it)",
        "body": "True story.\n\nOne of our clients was spending $8,500/month on Google Ads with a 1.8x ROAS. Technically above break-even, but barely.\n\nWe found that 60% of their budget was going to one keyword that had zero purchase intent.\n\nAfter fixing it: same spend, 4.2x ROAS.\n\nThat's the kind of thing our audit catches. Have you looked at yours yet?\n\n→ [Open your free audit]\n\nSarah\n\nP.S. This offer expires Friday.",
        "delay_days": 5,
    },
    {
        "subject": "Last call — your audit expires tonight",
        "body": "{{first_name}}, this is the last reminder.\n\nYour personalized audit expires at midnight tonight.\n\nIf growing your ROAS is a priority this quarter, take 10 minutes now.\n\n→ [Claim your audit before it expires]\n\nSarah",
        "delay_days": 7,
    },
    {
        "subject": "New case study: {{company}}-style win",
        "body": "Since you didn't grab the audit, I wanted to send you something valuable anyway.\n\nHere's a 3-minute case study showing how we helped a B2B SaaS company go from 1.9x to 5.4x ROAS in 45 days.\n\nNo audit required — just solid tactics you can steal.\n\n→ [Read the case study]\n\nHope it helps,\nSarah",
        "delay_days": 14,
    },
]

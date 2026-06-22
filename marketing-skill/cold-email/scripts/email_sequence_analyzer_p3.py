# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from email_sequence_analyzer_base import *  # noqa: F403,E402


def grade(score: int) -> str:
    if score >= 85:
        return "🟢 Strong"
    if score >= 65:
        return "🟡 Decent"
    if score >= 45:
        return "🟠 Needs work"
    return "🔴 Rewrite"
def print_report(results: List[Dict]) -> None:
    print("\n" + "═" * 64)
    print("  COLD EMAIL SEQUENCE ANALYSIS")
    print("═" * 64)

    scores = []
    for r in results:
        email_num = r["email"]
        subj = r["subject_analysis"]
        body = r["body_analysis"]
        overall = r["overall_score"]
        scores.append(overall)

        print(f"\n── Email {email_num}: \"{r['subject']}\" ──")
        print(f"   Overall: {overall}/100  {grade(overall)}")

        print(f"\n   Subject ({subj['length']} chars): {subj['score']}/100")
        for issue in subj.get("issues", []):
            print(f"   ❌ {issue}")
        for warn in subj.get("warnings", []):
            print(f"   ⚠️  {warn}")

        print(f"\n   Body Analysis:")
        print(f"   Words: {body['word_count']}  |  "
              f"Reading: {body['reading_level']}  |  "
              f"Avg sentence: {body['avg_words_per_sentence']} words  |  "
              f"Personalization density: {body['personalization_density']}%")
        print(f"   CTA: {'✅ Clear ask detected' if body['has_strong_cta'] else '❌ No clear CTA found'}")

        if body.get("spam_triggers"):
            print(f"   ⚠️  Spam triggers: {', '.join(body['spam_triggers'])}")

        if body.get("deductions"):
            print(f"\n   Issues found:")
            for desc, pts in body["deductions"]:
                print(f"   [-{pts:2d}] {desc}")

    avg = sum(scores) // len(scores) if scores else 0
    print(f"\n{'═' * 64}")
    print(f"  SEQUENCE OVERALL: {avg}/100  {grade(avg)}")
    print(f"  Emails analyzed: {len(results)}")

    # Sequence-level observations
    print("\n  Sequence observations:")
    word_counts = [r["body_analysis"]["word_count"] for r in results]
    if all(abs(word_counts[i] - word_counts[i-1]) < 20 for i in range(1, len(word_counts))):
        print("  ⚠️  All emails are similar length — vary length across sequence")

    if len(results) > 1:
        last_body = results[-1]["body_analysis"]
        if last_body["word_count"] > 100:
            print("  ⚠️  Final email (breakup) should be shorter — 3-5 sentences max")

    print("═" * 64 + "\n")
SAMPLE_SEQUENCE = [
    {
        "email": 1,
        "subject": "your SDR team expansion",
        "body": (
            "Saw you're hiring four SDRs simultaneously — that's a significant scale-up.\n\n"
            "The challenge most teams hit at this stage isn't recruiting — it's ramp time. "
            "When you're adding four people at once, the gaps in your onboarding process "
            "become very expensive very fast. The average ramp in your segment is around "
            "4.5 months; the fastest teams we've seen get it to 2.5.\n\n"
            "We've helped three similar-sized SaaS teams compress that gap. Happy to share "
            "what worked if it's useful.\n\n"
            "Worth 15 minutes to compare notes?"
        ),
    },
    {
        "email": 2,
        "subject": "re: your onboarding stack",
        "body": (
            "I hope this email finds you well. I wanted to follow up on my previous email.\n\n"
            "Just checking in to see if you had a chance to review what I sent. "
            "As mentioned, our platform offers a comprehensive suite of tools designed to "
            "help sales teams of all sizes achieve unprecedented growth through our "
            "revolutionary AI-powered onboarding solution.\n\n"
            "I'd love to schedule a 45-minute product demo at your earliest convenience. "
            "Please don't hesitate to reach out if you have any questions. "
            "I look forward to hearing from you!\n\n"
            "Click here to book a time: https://calendly.com/example"
        ),
    },
    {
        "email": 3,
        "subject": "SDR ramp benchmark",
        "body": (
            "One data point that might be useful: across the 40 SaaS teams we've benchmarked, "
            "the ones with the fastest SDR ramp time don't hire the most experienced reps — "
            "they invest more heavily in structured onboarding in the first 30 days.\n\n"
            "Happy to share the full breakdown. No catch — just thought it might be relevant "
            "given where you're headed.\n\n"
            "Useful?"
        ),
    },
    {
        "email": 4,
        "subject": "quick question",
        "body": (
            "Is SDR onboarding actually a priority right now, or is the timing just off?\n\n"
            "No judgment either way — just helps me know whether it's worth staying in touch."
        ),
    },
    {
        "email": 5,
        "subject": "last one",
        "body": (
            "I'll stop cluttering your inbox after this one.\n\n"
            "If scaling your SDR ramp time ever becomes a priority, happy to reconnect — "
            "just reply here.\n\n"
            "If there's someone else at your company who owns sales enablement, "
            "a name would go a long way.\n\n"
            "Either way, good luck with the expansion."
        ),
    },
]

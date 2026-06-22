# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sequence_analyzer_base import *  # noqa: F403,E402
# fmt: off
from sequence_analyzer_p1 import analyze_email, analyze_pacing  # noqa: E402,E501
from sequence_analyzer_p2 import DEMO_SEQUENCE, compute_sequence_score  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Email sequence analyzer — scores sequence quality 0-100."
    )
    parser.add_argument("--file", help="JSON file with email sequence array")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            emails = json.load(f)
    else:
        emails = DEMO_SEQUENCE
        if not args.json:
            print("No input provided — running in demo mode (5-email nurture sequence).\n")

    email_analyses = [analyze_email(e, i) for i, e in enumerate(emails)]
    pacing = analyze_pacing(emails)
    scoring = compute_sequence_score(email_analyses, pacing)

    if args.json:
        output = {
            "sequence_score": scoring,
            "pacing": pacing,
            "emails": email_analyses,
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable
    overall = scoring["overall"]
    grade = scoring["grade"]

    print("=" * 64)
    print(f"  EMAIL SEQUENCE ANALYSIS   Score: {overall}/100  Grade: {grade}")
    print("=" * 64)

    # Pacing summary
    print(f"\n  📅 SEQUENCE PACING")
    print(f"     Emails:         {pacing['email_count']}")
    print(f"     Duration:       {pacing.get('total_duration_days', 0)} days")
    print(f"     Avg gap:        {pacing.get('avg_gap_days', 0)} days")
    print(f"     Cadence:        {pacing.get('cadence_type', 'N/A')}")
    if pacing.get("issues"):
        for issue in pacing["issues"]:
            print(f"     ⚠️  {issue}")

    print(f"\n  📧 PER-EMAIL BREAKDOWN")
    print(f"  {'#':<3} {'Subject':<40} {'Words':<6} {'CTA':<4} {'Tokens':<7} {'Spam'}")
    print("  " + "─" * 60)

    for e in email_analyses:
        subj = e["subject"]["text"][:38]
        if not e["subject"]["length_ok"]:
            subj += "⚠️"
        words = e["body"]["word_count"]
        cta = "✅" if e["body"]["has_cta"] else "❌"
        tokens = e["body"]["personalization_tokens"]
        spam_lvl = e["spam"]["risk_level"]
        spam_icon = "✅" if spam_lvl == "Low" else ("⚠️ " if spam_lvl == "Medium" else "❌")
        spam_str = f"{spam_icon}{spam_lvl}"
        print(f"  {e['email_index']:<3} {subj:<40} {words:<6} {cta:<4} {tokens:<7} {spam_str}")

    if any(e["spam"]["trigger_words_found"] for e in email_analyses):
        print(f"\n  ⚠️  SPAM TRIGGER WORDS DETECTED")
        for e in email_analyses:
            if e["spam"]["trigger_words_found"]:
                triggers = ", ".join(e["spam"]["trigger_words_found"])
                print(f"     Email {e['email_index']}: {triggers}")

    print(f"\n  SCORE BREAKDOWN")
    for k, v in scoring["breakdown"].items():
        label = k.replace("_", " ").title()
        bar_len = round(v["score"] / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"  {label:<22} [{bar}] {v['score']:>3}/100  (weight {v['weight']})")

    print()
    print("=" * 64)
    print(f"  Overall: {overall}/100   Grade: {grade}")
    print("=" * 64)

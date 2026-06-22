# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from email_sequence_analyzer_base import *  # noqa: F403,E402
# fmt: off
from email_sequence_analyzer_p2 import analyze_body, analyze_subject_line  # noqa: E402,E501
from email_sequence_analyzer_p3 import SAMPLE_SEQUENCE, print_report  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyzes a cold email sequence for quality signals. "
                    "Evaluates word count, reading level, personalization, CTA clarity, "
                    "spam triggers, and subject lines. Scores each email 0-100."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a JSON file containing the email sequence. "
             "Use '-' to read from stdin. If omitted, runs embedded sample."
    )
    args = parser.parse_args()

    if args.file:
        if args.file == "-":
            sequence = json.load(sys.stdin)
        else:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    sequence = json.load(f)
            except FileNotFoundError:
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        print("No file provided — running on embedded sample sequence.\n")
        sequence = SAMPLE_SEQUENCE

    results = []
    for email in sequence:
        subject = email.get("subject", "")
        body = email.get("body", "")
        email_num = email.get("email", len(results) + 1)

        subject_analysis = analyze_subject_line(subject)
        body_analysis = analyze_body(body)

        # Overall score: 30% subject, 70% body
        overall = int(subject_analysis["score"] * 0.3 + body_analysis["score"] * 0.7)

        results.append({
            "email": email_num,
            "subject": subject,
            "subject_analysis": subject_analysis,
            "body_analysis": body_analysis,
            "overall_score": overall,
        })

    print_report(results)

    # JSON output for programmatic use
    summary = {
        "emails_analyzed": len(results),
        "average_score": sum(r["overall_score"] for r in results) // len(results) if results else 0,
        "results": [
            {
                "email": r["email"],
                "subject": r["subject"],
                "score": r["overall_score"],
                "word_count": r["body_analysis"]["word_count"],
                "has_strong_cta": r["body_analysis"]["has_strong_cta"],
                "spam_triggers": r["body_analysis"]["spam_triggers"],
                "subject_score": r["subject_analysis"]["score"],
            }
            for r in results
        ],
    }
    print("── JSON Output ──")
    print(json.dumps(summary, indent=2))

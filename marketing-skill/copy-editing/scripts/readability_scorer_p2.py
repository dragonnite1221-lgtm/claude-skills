# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from readability_scorer_base import *  # noqa: F403,E402
# fmt: off
from readability_scorer_p1 import analyze_text  # noqa: E402,E501
# fmt: on


DEMO_TEXT = """
Marketing copy needs to be clear, direct, and persuasive. When you write for your audience, 
you should always think about what they actually want to hear. Really good copy is basically 
about solving problems. It is very important to avoid using overly complicated language that 
might confuse the reader.

The best headlines are written by experts who truly understand their customers. A strong 
call-to-action is absolutely essential for any landing page. You need to make sure that 
every single word is earning its place on the page.

Studies show that shorter sentences improve comprehension. The average reader processes 
information faster when sentences contain fewer than 20 words. This is genuinely proven 
by research. Passive voice constructions are often used by writers who want to sound 
authoritative, but they can actually make copy feel distant and unclear.

Focus on benefits, not features. Tell the reader what they will gain. Use numbers when 
you can — "save 3 hours per week" beats "save time" every single time. Specificity 
builds trust. Vague promises are ignored.
"""
def main():
    parser = argparse.ArgumentParser(
        description="Readability scorer for marketing copy — Flesch, passive voice, filler words."
    )
    parser.add_argument("--file", help="Path to text file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        if not text.strip():
            text = DEMO_TEXT
            if not args.json:
                print("No input provided — running in demo mode.\n")
    else:
        text = DEMO_TEXT
        if not args.json:
            print("No input provided — running in demo mode.\n")

    result = analyze_text(text)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    fre = result["flesch_reading_ease"]
    fk = result["flesch_kincaid_grade"]
    stats = result["stats"]
    passive = result["passive_voice"]
    adverbs = result["adverb_density"]
    fillers = result["filler_words"]
    score = result["overall_score"]

    PASS = "✅"
    FAIL = "❌"

    print("=" * 62)
    print(f"  READABILITY REPORT   Flesch Score: {fre['score']}/100")
    print("=" * 62)
    print(f"  {fre['label']}")
    print(f"  Target: {fre['target']}")
    print()
    print(f"  📊 Stats")
    print(f"     Words:              {stats['word_count']}")
    print(f"     Sentences:          {stats['sentence_count']}")
    print(f"     Avg sentence length:{stats['avg_sentence_length']} words")
    print(f"     Avg word length:    {stats['avg_word_length']} chars")
    print(f"     Syllables/word:     {stats['avg_syllables_per_word']}")
    print()
    print(f"  📐 Flesch-Kincaid Grade Level: {fk['grade_level']}")
    print(f"     {fk['note']}")
    print()

    pv_icon = PASS if passive["pass"] else FAIL
    print(f"  {pv_icon} Passive Voice: {passive['count']} instances ({passive['percentage']}%)")
    print(f"     Target: {passive['target']}")

    av_icon = PASS if adverbs["pass"] else FAIL
    print(f"  {av_icon} Adverb Density: {adverbs['count']} adverbs ({adverbs['percentage']}%)")
    if adverbs["examples"]:
        print(f"     Examples: {', '.join(adverbs['examples'][:5])}")

    filler_ok = fillers["per_100_words"] <= 3
    fw_icon = PASS if filler_ok else FAIL
    print(f"  {fw_icon} Filler Words: {fillers['total_count']} total ({fillers['per_100_words']} per 100 words)")
    if fillers["breakdown"]:
        top = sorted(fillers["breakdown"].items(), key=lambda x: -x[1])[:5]
        print(f"     Top: {', '.join(f'{w}({c})' for w,c in top)}")

    print()
    print("=" * 62)
    score_bar_len = round(score / 10)
    bar = "█" * score_bar_len + "░" * (10 - score_bar_len)
    print(f"  Readability Score:  [{bar}] {score}/100")
    print("=" * 62)

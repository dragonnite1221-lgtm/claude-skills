# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_content_detector_base import *  # noqa: F403,E402
# fmt: off
from ai_content_detector_p1 import AI_PHRASES, AI_PHRASE_RES, DEMO_CONTENT, burstiness_score, extract_sentences, vocabulary_diversity  # noqa: E402,E501
# fmt: on


def phrase_detection(text):
    """Count known AI phrases."""
    found = []
    text_lower = text.lower()
    for i, pattern in enumerate(AI_PHRASE_RES):
        matches = pattern.findall(text_lower)
        if matches:
            found.append({"phrase": AI_PHRASES[i], "count": len(matches)})

    total_matches = sum(f["count"] for f in found)
    word_count = len(text.split())
    density = (total_matches / (word_count / 1000)) if word_count > 0 else 0

    # 0-2 per 1K words = normal; 3-5 = suspect; 6+ = likely AI
    if density <= 2:
        ai_prob = density * 15
    elif density <= 5:
        ai_prob = 30 + (density - 2) * 20
    else:
        ai_prob = min(100, 90 + (density - 5) * 5)

    return {
        "score": round(ai_prob, 1),
        "phrases_found": len(found),
        "total_matches": total_matches,
        "density_per_1k_words": round(density, 1),
        "matches": found[:10],
        "note": f"{density:.1f} AI phrases per 1K words" if found else "no known AI phrases",
    }
def _recommendations(burst, vocab, phrases):
    recs = []
    if burst["score"] > 40:
        recs.append("Vary sentence lengths: mix short punchy sentences (5-8 words) with longer explanatory ones (20-30 words).")
    if vocab["score"] > 40:
        recs.append("Diversify vocabulary: replace repeated words with synonyms. Use domain-specific jargon where appropriate.")
    if phrases["total_matches"] > 0:
        top = phrases["matches"][:3]
        recs.append(f"Remove/replace AI phrases: {', '.join(p['phrase'] for p in top)}")
    if not recs:
        recs.append("Content reads naturally. No humanization needed.")
    return recs
def analyze(text):
    sentences = extract_sentences(text)
    burst = burstiness_score(sentences)
    vocab = vocabulary_diversity(text)
    phrases = phrase_detection(text)

    # Weighted composite: burstiness 35%, vocab 30%, phrases 35%
    composite = burst["score"] * 0.35 + vocab["score"] * 0.30 + phrases["score"] * 0.35
    composite = round(min(100, max(0, composite)), 1)

    if composite <= 20:
        verdict = "LIKELY_HUMAN"
    elif composite <= 50:
        verdict = "MIXED"
    else:
        verdict = "LIKELY_AI"

    return {
        "status": "ok",
        "composite_score": composite,
        "verdict": verdict,
        "burstiness": burst,
        "vocabulary": vocab,
        "phrases": phrases,
        "sentences_analyzed": len(sentences),
        "recommendations": _recommendations(burst, vocab, phrases),
    }
def main():
    p = argparse.ArgumentParser(
        description="Detect AI-generated content via burstiness, vocabulary diversity, and phrase analysis.",
        epilog="Score 0-20 = likely human, 21-50 = mixed, 51-100 = likely AI. Run with --demo.",
    )
    p.add_argument("file", nargs="?", help="Markdown/text file to analyze")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--demo", action="store_true", help="Run with AI-heavy demo text")
    args = p.parse_args()

    if args.demo:
        text = DEMO_CONTENT
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"[error] {path} not found", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        p.print_help()
        sys.exit(0)

    result = analyze(text)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"AI Content Detection — Composite: {result['composite_score']}/100 ({result['verdict']})")
    print()
    b = result["burstiness"]
    print(f"  Burstiness:  {b['score']}/100 — CV={b['coefficient_of_variation']} ({b['note']})")
    v = result["vocabulary"]
    print(f"  Vocabulary:  {v['score']}/100 — TTR={v['avg_ttr']} ({v['note']})")
    ph = result["phrases"]
    print(f"  AI Phrases:  {ph['score']}/100 — {ph['total_matches']} matches, {ph['density_per_1k_words']}/1K words")
    if ph["matches"]:
        for m in ph["matches"][:5]:
            print(f"    → \"{m['phrase']}\" (×{m['count']})")
    print()
    print("Recommendations:")
    for r in result["recommendations"]:
        print(f"  → {r}")

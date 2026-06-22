# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_scorer_base import *  # noqa: F403,E402


def print_report(result: dict, title: str, keyword: str) -> None:
    total = result["total_score"]
    grade = result["grade"]
    s = result["sections"]

    bar_filled = int(total / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    print()
    print("╔══════════════════════════════════════════╗")
    print("║         CONTENT SCORER — REPORT          ║")
    print("╚══════════════════════════════════════════╝")
    print(f"  Title:   {title[:55] or '(not provided)'}")
    print(f"  Keyword: {keyword or '(not provided)'}")
    print()
    print(f"  TOTAL SCORE:  {total}/100  [{grade}]")
    print(f"  [{bar}]")
    print()
    print("  ── Section Breakdown ──────────────────────")

    sections = [
        ("Readability", s["readability"]),
        ("SEO Signals", s["seo"]),
        ("Structure",   s["structure"]),
        ("Engagement",  s["engagement"]),
    ]
    for label, section in sections:
        sc = section["score"]
        mx = section["max"]
        bar2_filled = int(sc / mx * 10)
        bar2 = "█" * bar2_filled + "░" * (10 - bar2_filled)
        print(f"  {label:<14} {sc:>2}/{mx}  [{bar2}]")

    print()
    print("  ── Key Signals ────────────────────────────")

    r = s["readability"]
    print(f"  Flesch Reading Ease:   {r['flesch_reading_ease']} (target: 60-70)")
    print(f"  Sentence length StDev: {r['sentence_length_std_dev']} (higher = more varied)")

    seo_d = s["seo"]
    print(f"  Keyword in title:      {'✅' if seo_d.get('keyword_in_title') else '❌'}")
    print(f"  Keyword in intro:      {'✅' if seo_d.get('keyword_in_intro') else '❌'}")
    print(f"  Keyword density:       {seo_d.get('keyword_density_pct', 0)}% (target: 0.5-2.5%)")
    print(f"  H2 sections:           {seo_d.get('h2_count', 0)}")

    st = s["structure"]
    print(f"  Intro word count:      {st.get('intro_word_count', 0)} (target: 30-200)")
    print(f"  Avg paragraph length:  {st.get('avg_paragraph_word_count', 0)} words (target: ≤80)")

    en = s["engagement"]
    print(f"  Questions:             {en.get('question_count', 0)}")
    print(f"  Stats/numbers:         {en.get('numbers_and_stats', 0)}")
    print(f"  Examples:              {en.get('example_signals', 0)}")

    print()
    print("  ── Recommendations ────────────────────────")
    if r["flesch_reading_ease"] < 55:
        print("  ⚠ Readability is low — shorten sentences and use simpler words")
    if not seo_d.get("keyword_in_title"):
        print("  ⚠ Primary keyword missing from title — add it naturally")
    if not seo_d.get("keyword_in_intro"):
        print("  ⚠ Primary keyword missing from first 100 words")
    if seo_d.get("h2_count", 0) < 3:
        print("  ⚠ Add more H2 sections — aim for at least 4")
    if st.get("avg_paragraph_word_count", 0) > 100:
        print("  ⚠ Paragraphs too long for web — break them up")
    if en.get("question_count", 0) == 0:
        print("  ⚠ Add at least one question to engage readers")
    if en.get("numbers_and_stats", 0) < 2:
        print("  ⚠ Thin on data — add specific numbers or stats")
    if total >= 70:
        print("  ✅ Content is publish-ready (score ≥ 70)")
    else:
        print(f"  ❌ Score below 70 — address recommendations before publishing")

    print()

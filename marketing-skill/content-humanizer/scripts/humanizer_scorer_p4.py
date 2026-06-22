# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from humanizer_scorer_base import *  # noqa: F403,E402


def print_report(result: dict, label: str = "") -> None:
    total = result["humanity_score"]
    verdict = result["label"]
    s = result["sections"]

    bar_filled = int(total / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    print()
    print("╔══════════════════════════════════════════╗")
    print("║       HUMANIZER SCORER — REPORT          ║")
    print("╚══════════════════════════════════════════╝")
    if label:
        print(f"  Input: {label}")
    print()
    print(f"  HUMANITY SCORE:  {total}/100")
    print(f"  [{bar}]")
    print(f"  Verdict: {verdict}")
    print()
    print("  ── Section Breakdown ──────────────────────")

    sections = [
        ("AI Vocabulary",      s["ai_vocabulary"],       25),
        ("Sentence Variance",  s["sentence_variance"],   20),
        ("Passive Voice",      s["passive_voice"],        20),
        ("Hedging Phrases",    s["hedging"],              15),
        ("Em-Dash Use",        s["em_dashes"],            10),
        ("Paragraph Variety",  s["paragraph_variety"],   10),
    ]
    for name, sec, mx in sections:
        sc = sec["score"]
        bar2 = "█" * int(sc / mx * 10) + "░" * (10 - int(sc / mx * 10))
        print(f"  {name:<20} {sc:>2}/{mx}  [{bar2}]")

    print()
    print("  ── Detected Issues ────────────────────────")

    v = s["ai_vocabulary"]
    if v["ai_word_hits"] > 0:
        terms = ", ".join(v["flagged_terms"][:5])
        print(f"  🔴 AI vocabulary: {v['ai_word_hits']} hits — [{terms}]")
    else:
        print("  ✅ No AI vocabulary detected")

    sv = s["sentence_variance"]
    if sv["std_dev"] < 5:
        print(f"  🔴 Sentence rhythm robotic — std dev only {sv['std_dev']} (target: 8+)")
    elif sv["std_dev"] < 8:
        print(f"  🟡 Sentence variance low — {sv['std_dev']} (target: 8+)")
    else:
        print(f"  ✅ Sentence variance good — {sv['std_dev']}")

    pv = s["passive_voice"]
    if pv["passive_ratio"] > 0.3:
        print(f"  🔴 Passive voice overuse — {pv['passive_pct']} of sentences")
    elif pv["passive_ratio"] > 0.2:
        print(f"  🟡 Passive voice elevated — {pv['passive_pct']}")
    else:
        print(f"  ✅ Passive voice in range — {pv['passive_pct']}")

    hg = s["hedging"]
    if hg["hedge_count"] > 2:
        terms = ", ".join(hg["flagged_phrases"][:3])
        print(f"  🔴 Hedging overload — {hg['hedge_count']} phrases: [{terms}]")
    elif hg["hedge_count"] > 0:
        print(f"  🟡 Hedging present — {hg['hedge_count']} phrase(s): {hg['flagged_phrases']}")
    else:
        print("  ✅ No hedging detected")

    if hg["vague_authority_count"] > 0:
        print(f"  🟡 Vague authority claims: {hg['vague_authority_count']} (e.g. 'studies show') — add citations")

    em = s["em_dashes"]
    if em["per_100_words"] > 3:
        print(f"  🟡 Em-dash overuse — {em['em_dash_count']} in piece ({em['per_100_words']}/100 words)")

    pg = s["paragraph_variety"]
    if not pg.get("has_short_paragraphs"):
        print("  🟡 No short paragraphs found — add some 1-2 sentence paragraphs for rhythm")

    print()
    print("  ── Priority Fixes ─────────────────────────")

    if v["ai_word_hits"] > 5:
        print("  1. Replace AI vocabulary (biggest impact)")
    if sv["std_dev"] < 8:
        print("  2. Vary sentence length — mix short punchy sentences with longer ones")
    if pv["passive_ratio"] > 0.25:
        print("  3. Flip passive sentences to active voice")
    if hg["hedge_count"] > 2:
        print("  4. Cut hedging phrases — state claims directly")
    if not pg.get("has_short_paragraphs"):
        print("  5. Add short paragraphs — even 1-sentence paragraphs help rhythm")

    if total >= 85:
        print("  ✅ No priority fixes — content reads as human")
    print()

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_tracker_base import *  # noqa: F403,E402
# fmt: off
from decision_tracker_p1 import Decision  # noqa: E402,E501
from decision_tracker_p2 import fmt_date, print_section  # noqa: E402,E501
# fmt: on


def report_conflicts(decisions: list[Decision]):
    """
    Simple conflict detection: look for decisions on the same topic
    (matching title words) that are both active and have different decisions.
    Also flag if a rejected item appears as a new decision.
    """
    print_section("CONFLICT DETECTION")
    conflicts_found = False

    # Check for DO_NOT_RESURFACE violations
    all_rejected_texts = []
    for d in decisions:
        for r in d.rejected:
            clean = re.sub(r"\[DO_NOT_RESURFACE\]", "", r).strip().lower()
            all_rejected_texts.append((clean, d.date, d.title))

    active = [d for d in decisions if d.is_active()]
    for d in active:
        decision_lower = d.decision.lower()
        for rejected_text, rejected_date, rejected_title in all_rejected_texts:
            if rejected_text and rejected_text in decision_lower:
                conflicts_found = True
                print(f"\n  🚫 POTENTIAL DO_NOT_RESURFACE VIOLATION")
                print(f"    Decision [{fmt_date(d.date)}]: {d.decision}")
                print(f"    Matches rejected item from [{fmt_date(rejected_date)}] ({rejected_title}):")
                print(f"    \"{rejected_text}\"")

    # Check for same-topic contradictions (shared keywords in title)
    stop_words = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with", "vs"}
    for i, d1 in enumerate(active):
        words1 = set(w.lower() for w in d1.title.split() if w.lower() not in stop_words)
        for d2 in active[i+1:]:
            words2 = set(w.lower() for w in d2.title.split() if w.lower() not in stop_words)
            overlap = words1 & words2
            if len(overlap) >= 2 and d1.decision and d2.decision:
                # Different decisions on similar topic
                if d1.decision.lower() != d2.decision.lower():
                    conflicts_found = True
                    print(f"\n  ⚠️  POTENTIAL CONFLICT (shared topic: {overlap})")
                    print(f"    [{fmt_date(d1.date)}] {d1.title}")
                    print(f"    Decision: {d1.decision}")
                    print(f"    [{fmt_date(d2.date)}] {d2.title}")
                    print(f"    Decision: {d2.decision}")
                    if d1.superseded_by or d2.superseded_by:
                        print(f"    ℹ️  One may supersede the other — check Superseded by fields.")

    if not conflicts_found:
        print("\n  ✅ No conflicts detected.")
SAMPLE_DECISIONS_MD = f"""# Board Meeting Decisions — Layer 2

This file contains ONLY founder-approved decisions.

---

## 2026-02-15 — Spain Market Expansion

**Decision:** Expand to Spain in Q3 2026 with a pilot in Madrid and Barcelona.
**Owner:** CMO
**Deadline:** 2026-03-01
**Review:** 2026-04-01
**Rationale:** Market research shows 40% lower CAC than Germany. Two pilot customers already committed.

**User Override:** Founder reduced pilot scope from 5 cities to 2. Reason: reduce operational risk during expansion.

**Rejected:**
- Launch in all of Spain simultaneously — too resource-intensive at current headcount [DO_NOT_RESURFACE]
- Partner with a local distributor instead of direct sales — margins too low [DO_NOT_RESURFACE]

**Action Items:**
- [x] Hire Spanish-speaking CSM — Owner: CHRO — Completed: 2026-02-28 — Result: Hired Maria G., starts March 10
- [ ] Finalize Madrid pilot customer contracts — Owner: CRO — Due: {(date.today() - timedelta(days=3)).strftime('%Y-%m-%d')} — Review: 2026-04-01
- [ ] Translate app to Spanish (ES-ES) — Owner: CTO — Due: {(date.today() + timedelta(days=5)).strftime('%Y-%m-%d')} — Review: 2026-04-15

**Supersedes:** 
**Superseded by:** 
**Raw transcript:** memory/board-meetings/2026-02-15-raw.md

---

## 2026-02-28 — Pricing Strategy Revision

**Decision:** Move from per-seat to usage-based pricing effective Q2 2026.
**Owner:** CFO
**Deadline:** 2026-03-20
**Review:** 2026-05-01
**Rationale:** Usage-based aligns with customer value. Three enterprise customers requested it explicitly.

**User Override:** 

**Rejected:**
- Freemium tier — not appropriate for enterprise healthcare segment [DO_NOT_RESURFACE]
- Raise prices 30% across the board — too aggressive without usage data [DO_NOT_RESURFACE]

**Action Items:**
- [ ] Model 3 pricing scenarios (conservative/base/aggressive) — Owner: CFO — Due: {(date.today() - timedelta(days=1)).strftime('%Y-%m-%d')} — Review: 2026-03-25
- [ ] Customer interviews on usage patterns (n=10) — Owner: CMO — Due: {(date.today() + timedelta(days=10)).strftime('%Y-%m-%d')} — Review: 2026-04-01
- [ ] Update billing infrastructure for usage tracking — Owner: CTO — Due: 2026-04-01 — Review: 2026-04-15

**Supersedes:** 
**Superseded by:** 
**Raw transcript:** memory/board-meetings/2026-02-28-raw.md

---

## 2026-03-04 — Engineering Hiring Plan Q2

**Decision:** Hire 2 senior engineers in Q2: one ML/AI, one backend. No contractors.
**Owner:** CTO
**Deadline:** 2026-04-15
**Review:** 2026-05-01
**Rationale:** ML roadmap blocked. Backend capacity at 85%. Contractors rejected due to IP risk in regulated domain.

**User Override:** Founder added: "ML hire must have healthcare AI experience. Non-negotiable."

**Rejected:**
- Contract team of 5 for 3 months — IP risk in regulated domain [DO_NOT_RESURFACE]
- Hire junior engineers to save budget — wrong tradeoff at this stage [DO_NOT_RESURFACE]

**Action Items:**
- [ ] Post ML engineer JD — Owner: CHRO — Due: {(date.today() + timedelta(days=2)).strftime('%Y-%m-%d')} — Review: 2026-03-20
- [ ] Post backend engineer JD — Owner: CHRO — Due: {(date.today() + timedelta(days=2)).strftime('%Y-%m-%d')} — Review: 2026-03-20
- [ ] Define ML role requirements with healthcare AI spec — Owner: CTO — Due: {(date.today() + timedelta(days=1)).strftime('%Y-%m-%d')} — Review: 2026-03-15

**Supersedes:** 
**Superseded by:** 
**Raw transcript:** memory/board-meetings/2026-03-04-raw.md
"""

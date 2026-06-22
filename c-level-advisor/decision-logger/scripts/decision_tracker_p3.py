# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_tracker_base import *  # noqa: F403,E402
# fmt: off
from decision_tracker_p1 import Decision  # noqa: E402,E501
from decision_tracker_p2 import fmt_date, fmt_delta, print_section  # noqa: E402,E501
# fmt: on


def report_summary(decisions: list[Decision]):
    active = [d for d in decisions if d.is_active()]
    all_actions = [a for d in decisions for a in d.action_items]
    open_actions = [a for a in all_actions if not a.completed]
    overdue = [a for a in all_actions if a.is_overdue()]
    overrides = [d for d in decisions if d.has_override()]
    dnr_count = sum(len(d.rejected) for d in decisions)

    print_section("DECISION LOG SUMMARY")
    print(f"  Total decisions:      {len(decisions)}")
    print(f"  Active (not super.):  {len(active)}")
    print(f"  Superseded:           {len(decisions) - len(active)}")
    print(f"  Founder overrides:    {len(overrides)}")
    print(f"  DO_NOT_RESURFACE:     {dnr_count}")
    print(f"  Total action items:   {len(all_actions)}")
    print(f"  Open action items:    {len(open_actions)}")
    print(f"  Overdue:              {len(overdue)}")

    if overdue:
        print(f"\n  {'─' * 40}")
        print(f"  ⚠️  OVERDUE ITEMS ({len(overdue)})")
        print(f"  {'─' * 40}")
        for a in overdue:
            print(f"  • [{a.owner}] {a.text}")
            print(f"    Due: {fmt_date(a.due)}{fmt_delta(a.due)}")

    print(f"\n  {'─' * 40}")
    print(f"  RECENT DECISIONS")
    print(f"  {'─' * 40}")
    for d in sorted(active, key=lambda x: x.date or date.min, reverse=True)[:5]:
        print(f"  [{fmt_date(d.date)}] {d.title}")
        print(f"    Owner: {d.owner or '—'}  |  Deadline: {fmt_date(d.deadline)}")
        open_count = sum(1 for a in d.action_items if not a.completed)
        if open_count:
            print(f"    Open actions: {open_count}")
def report_overdue(decisions: list[Decision]):
    print_section("OVERDUE ACTION ITEMS")
    found = False
    for d in sorted(decisions, key=lambda x: x.date or date.min, reverse=True):
        overdue = [a for a in d.action_items if a.is_overdue()]
        if not overdue:
            continue
        found = True
        print(f"\n  📋 {d.title}  [{fmt_date(d.date)}]")
        for a in overdue:
            print(f"    ⚠️  {a.text}")
            print(f"       Owner: {a.owner or '—'}  |  Due: {fmt_date(a.due)}{fmt_delta(a.due)}")
    if not found:
        print("\n  ✅ No overdue items.")
def report_due_within(decisions: list[Decision], days: int):
    print_section(f"ACTION ITEMS DUE WITHIN {days} DAYS")
    found = False
    for d in sorted(decisions, key=lambda x: x.date or date.min, reverse=True):
        upcoming = [a for a in d.action_items if a.is_due_within(days)]
        if not upcoming:
            continue
        found = True
        print(f"\n  📋 {d.title}  [{fmt_date(d.date)}]")
        for a in upcoming:
            print(f"    • {a.text}")
            print(f"      Owner: {a.owner or '—'}  |  Due: {fmt_date(a.due)}{fmt_delta(a.due)}")
    if not found:
        print(f"\n  ✅ Nothing due in the next {days} days.")
def report_by_owner(decisions: list[Decision], owner: str):
    print_section(f"ACTION ITEMS — OWNER: {owner.upper()}")
    found = False
    for d in sorted(decisions, key=lambda x: x.date or date.min, reverse=True):
        items = [a for a in d.action_items
                 if a.owner.lower() == owner.lower() and not a.completed]
        if not items:
            continue
        found = True
        print(f"\n  📋 {d.title}  [{fmt_date(d.date)}]")
        for a in items:
            flag = "⚠️ OVERDUE" if a.is_overdue() else ""
            print(f"    {'[ ]'} {a.text}  {flag}")
            print(f"      Due: {fmt_date(a.due)}{fmt_delta(a.due)}")
    if not found:
        print(f"\n  No open action items for '{owner}'.")
def report_search(decisions: list[Decision], query: str):
    print_section(f"SEARCH: \"{query}\"")
    q = query.lower()
    found = False
    for d in decisions:
        hit_fields = []
        if q in d.title.lower():
            hit_fields.append("title")
        if q in d.decision.lower():
            hit_fields.append("decision")
        if q in d.rationale.lower():
            hit_fields.append("rationale")
        if any(q in r.lower() for r in d.rejected):
            hit_fields.append("rejected")
        if hit_fields:
            found = True
            print(f"\n  [{fmt_date(d.date)}] {d.title}  (match: {', '.join(hit_fields)})")
            if "decision" in hit_fields:
                print(f"    → {d.decision}")
            if "rejected" in hit_fields:
                matches = [r for r in d.rejected if q in r.lower()]
                for r in matches:
                    print(f"    ✗ [REJECTED] {r}")
    if not found:
        print(f"\n  No results for '{query}'.")

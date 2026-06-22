# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_tracker_base import *  # noqa: F403,E402
# fmt: off
from decision_tracker_p1 import Decision, parse_action_item, parse_date  # noqa: E402,E501
# fmt: on


def parse_decisions(content: str) -> list[Decision]:
    """Parse the full decisions.md content into Decision objects."""
    decisions = []
    current: Optional[Decision] = None
    in_rejected = False
    in_actions = False

    for line in content.splitlines():
        # New decision entry
        header_match = re.match(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", line)
        if header_match:
            if current:
                decisions.append(current)
            current = Decision()
            current.date = parse_date(header_match.group(1))
            current.title = header_match.group(2).strip()
            in_rejected = False
            in_actions = False
            continue

        if current is None:
            continue

        # Field parsing
        def extract_field(label: str) -> Optional[str]:
            pattern = rf"^\*\*{re.escape(label)}:\*\*\s*(.*)$"
            m = re.match(pattern, line)
            return m.group(1).strip() if m else None

        val = extract_field("Decision")
        if val is not None:
            current.decision = val
            in_rejected = False
            in_actions = False
            continue

        val = extract_field("Owner")
        if val is not None:
            current.owner = val
            continue

        val = extract_field("Deadline")
        if val is not None:
            current.deadline = parse_date(val)
            continue

        val = extract_field("Review")
        if val is not None:
            current.review = parse_date(val)
            continue

        val = extract_field("Rationale")
        if val is not None:
            current.rationale = val
            continue

        val = extract_field("User Override")
        if val is not None:
            current.user_override = val
            in_rejected = False
            in_actions = False
            continue

        val = extract_field("Supersedes")
        if val is not None:
            current.supersedes = val
            continue

        val = extract_field("Superseded by")
        if val is not None:
            current.superseded_by = val
            continue

        val = extract_field("Raw transcript")
        if val is not None:
            current.raw_transcript = val
            continue

        # Section headers
        if re.match(r"^\*\*Rejected:\*\*", line):
            in_rejected = True
            in_actions = False
            continue

        if re.match(r"^\*\*Action Items:\*\*", line):
            in_actions = True
            in_rejected = False
            continue

        if line.startswith("**"):
            in_rejected = False
            in_actions = False

        # List items
        if in_rejected and line.strip().startswith("-"):
            item = line.strip().lstrip("- ").strip()
            if item and not item.startswith("<!--"):
                current.rejected.append(item)
            continue

        if in_actions and line.strip().startswith("- ["):
            action = parse_action_item(line)
            if action:
                current.action_items.append(action)
            continue

    if current:
        decisions.append(current)

    return decisions
def fmt_date(d: Optional[date]) -> str:
    return d.strftime("%Y-%m-%d") if d else "—"
def fmt_delta(d: Optional[date]) -> str:
    if not d:
        return ""
    delta = (d - date.today()).days
    if delta < 0:
        return f"  ⚠️  {abs(delta)}d overdue"
    if delta == 0:
        return "  🔴 DUE TODAY"
    if delta <= 3:
        return f"  🟡 {delta}d left"
    return f"  ({delta}d)"
def print_section(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")

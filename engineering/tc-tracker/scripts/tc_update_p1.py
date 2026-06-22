# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_update_base import *  # noqa: F403,E402


VALID_STATUSES = ("planned", "in_progress", "blocked", "implemented", "tested", "deployed")
VALID_TRANSITIONS = {
    "planned":     ["in_progress", "blocked"],
    "in_progress": ["blocked", "implemented"],
    "blocked":     ["in_progress", "planned"],
    "implemented": ["tested", "in_progress"],
    "tested":      ["deployed", "in_progress"],
    "deployed":    ["in_progress"],
}
VALID_FILE_ACTIONS = ("created", "modified", "deleted", "renamed")
VALID_TEST_STATUSES = ("pending", "pass", "fail", "skip", "blocked")
VALID_SCOPES = ("feature", "bugfix", "refactor", "infrastructure", "documentation", "hotfix", "enhancement")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
def write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
def find_record_path(tc_dir: Path, tc_id: str) -> Path | None:
    direct = tc_dir / "records" / tc_id / "tc_record.json"
    if direct.exists():
        return direct
    for entry in (tc_dir / "records").glob("*"):
        if entry.is_dir() and entry.name.startswith(tc_id):
            candidate = entry / "tc_record.json"
            if candidate.exists():
                return candidate
    return None
def validate_transition(current: str, new: str) -> str | None:
    if current == new:
        return None
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        return f"Invalid transition '{current}' -> '{new}'. Allowed: {', '.join(allowed) or 'none'}"
    return None
def next_revision_id(record: dict) -> str:
    return f"R{len(record.get('revision_history', [])) + 1}"
def next_test_id(record: dict) -> str:
    return f"T{len(record.get('test_cases', [])) + 1}"
def compute_stats(records: list) -> dict:
    stats = {
        "total": len(records),
        "by_status": {s: 0 for s in VALID_STATUSES},
        "by_scope": {s: 0 for s in VALID_SCOPES},
        "by_priority": {p: 0 for p in VALID_PRIORITIES},
    }
    for rec in records:
        for key, bucket in (("status", "by_status"), ("scope", "by_scope"), ("priority", "by_priority")):
            v = rec.get(key, "")
            if v in stats[bucket]:
                stats[bucket][v] += 1
    return stats
def parse_file_arg(spec: str) -> tuple[str, str]:
    """Parse 'path:action' or just 'path' (default action: modified)."""
    if ":" in spec:
        path, action = spec.rsplit(":", 1)
        action = action.strip()
        if action not in VALID_FILE_ACTIONS:
            raise ValueError(f"Invalid file action '{action}'. Must be one of {VALID_FILE_ACTIONS}")
        return path.strip(), action
    return spec.strip(), "modified"
def _csd_0(args, field_changes, record, summary_parts, ts):
    handoff = record.setdefault("session_context", {}).setdefault("handoff", {
        "progress_summary": "", "next_steps": [], "blockers": [],
        "key_context": [], "files_in_progress": [], "decisions_made": [],
    })

    if args.handoff_progress is not None:
        old = handoff.get("progress_summary", "")
        handoff["progress_summary"] = args.handoff_progress
        field_changes.append({
            "field": "session_context.handoff.progress_summary",
            "action": "changed", "old_value": old, "new_value": args.handoff_progress,
            "reason": args.reason or None,
        })
        summary_parts.append("handoff: updated progress_summary")

    for step in args.handoff_next:
        handoff.setdefault("next_steps", []).append(step)
        field_changes.append({
            "field": "session_context.handoff.next_steps",
            "action": "added", "new_value": step, "reason": args.reason or None,
        })
        summary_parts.append(f"handoff: +next_step '{step}'")

    for blk in args.handoff_blocker:
        handoff.setdefault("blockers", []).append(blk)
        field_changes.append({
            "field": "session_context.handoff.blockers",
            "action": "added", "new_value": blk, "reason": args.reason or None,
        })
        summary_parts.append(f"handoff: +blocker '{blk}'")

    for ctx in args.handoff_context:
        handoff.setdefault("key_context", []).append(ctx)
        field_changes.append({
            "field": "session_context.handoff.key_context",
            "action": "added", "new_value": ctx, "reason": args.reason or None,
        })
        summary_parts.append(f"handoff: +context")

    if args.note:
        existing = record.get("notes", "") or ""
        addition = f"[{ts}] {args.note}"
        record["notes"] = (existing + "\n" + addition).strip() if existing else addition
        field_changes.append({
            "field": "notes", "action": "added",
            "new_value": args.note, "reason": args.reason or None,
        })
        summary_parts.append("note appended")

    for tag in args.tag:
        if tag not in record.setdefault("tags", []):
            record["tags"].append(tag)
            field_changes.append({
                "field": "tags", "action": "added",
                "new_value": tag, "reason": args.reason or None,
            })
            summary_parts.append(f"+tag {tag}")

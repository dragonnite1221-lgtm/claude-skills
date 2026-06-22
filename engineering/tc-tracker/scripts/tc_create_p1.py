# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_create_base import *  # noqa: F403,E402


VALID_STATUSES = ("planned", "in_progress", "blocked", "implemented", "tested", "deployed")
VALID_SCOPES = ("feature", "bugfix", "refactor", "infrastructure", "documentation", "hotfix", "enhancement")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
def date_slug(dt: datetime) -> str:
    return dt.strftime("%m-%d-%y")
def write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
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
def build_record(tc_id: str, title: str, scope: str, priority: str, summary: str,
                 motivation: str, project_name: str, author: str, session_id: str,
                 platform: str, model: str) -> dict:
    ts = now_iso()
    return {
        "tc_id": tc_id,
        "parent_tc": None,
        "title": title,
        "status": "planned",
        "priority": priority,
        "created": ts,
        "updated": ts,
        "created_by": author,
        "project": project_name,
        "description": {
            "summary": summary,
            "motivation": motivation,
            "scope": scope,
            "detailed_design": None,
            "breaking_changes": [],
            "dependencies": [],
        },
        "files_affected": [],
        "revision_history": [
            {
                "revision_id": "R1",
                "timestamp": ts,
                "author": author,
                "summary": "TC record created",
                "field_changes": [
                    {"field": "status", "action": "set", "new_value": "planned", "reason": "initial creation"},
                ],
            }
        ],
        "sub_tcs": [],
        "test_cases": [],
        "approval": {
            "approved": False,
            "approved_by": None,
            "approved_date": None,
            "approval_notes": "",
            "test_coverage_status": "none",
        },
        "session_context": {
            "current_session": {
                "session_id": session_id,
                "platform": platform,
                "model": model,
                "started": ts,
                "last_active": ts,
            },
            "handoff": {
                "progress_summary": "",
                "next_steps": [],
                "blockers": [],
                "key_context": [],
                "files_in_progress": [],
                "decisions_made": [],
            },
            "session_history": [],
        },
        "tags": [],
        "related_tcs": [],
        "notes": "",
        "metadata": {
            "project": project_name,
            "created_by": author,
            "last_modified_by": author,
            "last_modified": ts,
            "estimated_effort": None,
        },
    }

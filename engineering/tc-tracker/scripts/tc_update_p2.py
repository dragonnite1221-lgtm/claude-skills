# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_update_base import *  # noqa: F403,E402
# fmt: off
from tc_update_p1 import VALID_STATUSES, _csd_0, compute_stats, find_record_path, next_revision_id, next_test_id, now_iso, parse_file_arg, validate_transition, write_json_atomic  # noqa: E402,E501
# fmt: on


def main() -> int:
    parser = argparse.ArgumentParser(description="Update an existing TC record.")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument("--tc-id", required=True, help="Target TC ID (full or prefix)")
    parser.add_argument("--author", default=None, help="Author for this revision (defaults to config)")
    parser.add_argument("--reason", default="", help="Reason for the change (recorded in revision)")

    parser.add_argument("--set-status", choices=VALID_STATUSES, help="Transition status (state machine enforced)")
    parser.add_argument("--add-file", action="append", default=[], metavar="path[:action]",
                        help="Add a file. Action defaults to 'modified'. Repeatable.")
    parser.add_argument("--add-test", help="Add a test case with this title")
    parser.add_argument("--test-procedure", action="append", default=[],
                        help="Procedure step for the test being added. Repeatable.")
    parser.add_argument("--test-expected", help="Expected result for the test being added")

    parser.add_argument("--handoff-progress", help="Set progress_summary in handoff")
    parser.add_argument("--handoff-next", action="append", default=[], help="Append to next_steps. Repeatable.")
    parser.add_argument("--handoff-blocker", action="append", default=[], help="Append to blockers. Repeatable.")
    parser.add_argument("--handoff-context", action="append", default=[], help="Append to key_context. Repeatable.")

    parser.add_argument("--note", help="Append a freeform note (with timestamp)")
    parser.add_argument("--tag", action="append", default=[], help="Add a tag. Repeatable.")

    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    tc_dir = root / "docs" / "TC"
    config_path = tc_dir / "tc_config.json"
    registry_path = tc_dir / "tc_registry.json"

    if not config_path.exists() or not registry_path.exists():
        msg = f"TC tracking not initialized at {tc_dir}. Run tc_init.py first."
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    record_path = find_record_path(tc_dir, args.tc_id)
    if record_path is None:
        msg = f"TC not found: {args.tc_id}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        msg = f"Failed to read JSON: {e}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    author = args.author or config.get("default_author", "Claude")
    ts = now_iso()

    field_changes = []
    summary_parts = []

    if args.set_status:
        current = record.get("status")
        new = args.set_status
        err = validate_transition(current, new)
        if err:
            print(json.dumps({"status": "error", "error": err}) if args.json else f"ERROR: {err}")
            return 2
        if current != new:
            record["status"] = new
            field_changes.append({
                "field": "status", "action": "changed",
                "old_value": current, "new_value": new, "reason": args.reason or None,
            })
            summary_parts.append(f"status: {current} -> {new}")

    for spec in args.add_file:
        try:
            path, action = parse_file_arg(spec)
        except ValueError as e:
            print(json.dumps({"status": "error", "error": str(e)}) if args.json else f"ERROR: {e}")
            return 2
        record.setdefault("files_affected", []).append({
            "path": path, "action": action, "description": None,
            "lines_added": None, "lines_removed": None,
        })
        field_changes.append({
            "field": "files_affected", "action": "added",
            "new_value": {"path": path, "action": action},
            "reason": args.reason or None,
        })
        summary_parts.append(f"+file {path} ({action})")

    if args.add_test:
        if not args.test_procedure or not args.test_expected:
            msg = "--add-test requires at least one --test-procedure and --test-expected"
            print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
            return 2
        test_id = next_test_id(record)
        new_test = {
            "test_id": test_id,
            "title": args.add_test,
            "procedure": list(args.test_procedure),
            "expected_result": args.test_expected,
            "actual_result": None,
            "status": "pending",
            "evidence": [],
            "tested_by": None,
            "tested_date": None,
        }
        record.setdefault("test_cases", []).append(new_test)
        field_changes.append({
            "field": "test_cases", "action": "added",
            "new_value": test_id, "reason": args.reason or None,
        })
        summary_parts.append(f"+test {test_id}: {args.add_test}")

    _csd_0(args, field_changes, record, summary_parts, ts)

    if not field_changes:
        msg = "No changes specified. Use --set-status, --add-file, --add-test, --handoff-*, --note, or --tag."
        print(json.dumps({"status": "noop", "message": msg}) if args.json else msg)
        return 0

    revision = {
        "revision_id": next_revision_id(record),
        "timestamp": ts,
        "author": author,
        "summary": "; ".join(summary_parts) if summary_parts else "TC updated",
        "field_changes": field_changes,
    }
    record.setdefault("revision_history", []).append(revision)

    record["updated"] = ts
    meta = record.setdefault("metadata", {})
    meta["last_modified"] = ts
    meta["last_modified_by"] = author

    cs = record.setdefault("session_context", {}).setdefault("current_session", {})
    cs["last_active"] = ts

    try:
        write_json_atomic(record_path, record)
    except OSError as e:
        msg = f"Failed to write record: {e}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    for entry in registry.get("records", []):
        if entry.get("tc_id") == record["tc_id"]:
            entry["status"] = record["status"]
            entry["updated"] = ts
            break
    registry["updated"] = ts
    registry["statistics"] = compute_stats(registry.get("records", []))

    try:
        write_json_atomic(registry_path, registry)
    except OSError as e:
        msg = f"Failed to update registry: {e}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    result = {
        "status": "updated",
        "tc_id": record["tc_id"],
        "revision": revision["revision_id"],
        "summary": revision["summary"],
        "current_status": record["status"],
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Updated {record['tc_id']} ({revision['revision_id']})")
        print(f"  {revision['summary']}")
        print(f"  Status: {record['status']}")

    return 0

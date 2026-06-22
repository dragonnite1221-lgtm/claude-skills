# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_validator_base import *  # noqa: F403,E402
# fmt: off
from tc_validator_p1 import REVISION_ID_PATTERN, TEST_ID_PATTERN, VALID_COVERAGE, VALID_FILE_ACTIONS, VALID_PLATFORMS, VALID_PRIORITIES, VALID_SCOPES, VALID_STATUSES, VALID_TEST_STATUSES, _enum, _iso, _required, _string, validate_tc_id  # noqa: E402,E501
# fmt: on


def validate_tc_record(record):
    """Validate a TC record dict against the schema."""
    errors = []
    if not isinstance(record, dict):
        return [f"TC record must be a JSON object, got {type(record).__name__}"]

    top_required = [
        "tc_id", "title", "status", "priority", "created", "updated",
        "created_by", "project", "description", "files_affected",
        "revision_history", "test_cases", "approval", "session_context",
        "tags", "related_tcs", "notes", "metadata",
    ]
    errors.extend(_required(record, top_required))

    if "tc_id" in record:
        errors.extend(validate_tc_id(record["tc_id"]))
    if "title" in record:
        errors.extend(_string(record["title"], "title", 5, 120))
    if "status" in record:
        errors.extend(_enum(record["status"], VALID_STATUSES, "status"))
    if "priority" in record:
        errors.extend(_enum(record["priority"], VALID_PRIORITIES, "priority"))
    for ts in ("created", "updated"):
        if ts in record:
            errors.extend(_iso(record[ts], ts))
    if "created_by" in record:
        errors.extend(_string(record["created_by"], "created_by", 1))
    if "project" in record:
        errors.extend(_string(record["project"], "project", 1))

    desc = record.get("description")
    if isinstance(desc, dict):
        errors.extend(_required(desc, ["summary", "motivation", "scope"], "description"))
        if "summary" in desc:
            errors.extend(_string(desc["summary"], "description.summary", 10))
        if "motivation" in desc:
            errors.extend(_string(desc["motivation"], "description.motivation", 1))
        if "scope" in desc:
            errors.extend(_enum(desc["scope"], VALID_SCOPES, "description.scope"))
    elif "description" in record:
        errors.append("Field 'description' must be an object")

    files = record.get("files_affected")
    if isinstance(files, list):
        for i, f in enumerate(files):
            prefix = f"files_affected[{i}]"
            if not isinstance(f, dict):
                errors.append(f"{prefix} must be an object")
                continue
            errors.extend(_required(f, ["path", "action"], prefix))
            if "action" in f:
                errors.extend(_enum(f["action"], VALID_FILE_ACTIONS, f"{prefix}.action"))
    elif "files_affected" in record:
        errors.append("Field 'files_affected' must be an array")

    revs = record.get("revision_history")
    if isinstance(revs, list):
        if len(revs) < 1:
            errors.append("revision_history must have at least 1 entry")
        for i, rev in enumerate(revs):
            prefix = f"revision_history[{i}]"
            if not isinstance(rev, dict):
                errors.append(f"{prefix} must be an object")
                continue
            errors.extend(_required(rev, ["revision_id", "timestamp", "author", "summary"], prefix))
            rid = rev.get("revision_id")
            if isinstance(rid, str):
                m = REVISION_ID_PATTERN.match(rid)
                if not m:
                    errors.append(f"{prefix}.revision_id '{rid}' must match R<n>")
                elif int(m.group(1)) != i + 1:
                    errors.append(f"{prefix}.revision_id is '{rid}' but expected 'R{i + 1}' (must be sequential)")
            if "timestamp" in rev:
                errors.extend(_iso(rev["timestamp"], f"{prefix}.timestamp"))
    elif "revision_history" in record:
        errors.append("Field 'revision_history' must be an array")

    tests = record.get("test_cases")
    if isinstance(tests, list):
        for i, tc in enumerate(tests):
            prefix = f"test_cases[{i}]"
            if not isinstance(tc, dict):
                errors.append(f"{prefix} must be an object")
                continue
            errors.extend(_required(tc, ["test_id", "title", "procedure", "expected_result", "status"], prefix))
            tid = tc.get("test_id")
            if isinstance(tid, str):
                m = TEST_ID_PATTERN.match(tid)
                if not m:
                    errors.append(f"{prefix}.test_id '{tid}' must match T<n>")
                elif int(m.group(1)) != i + 1:
                    errors.append(f"{prefix}.test_id is '{tid}' but expected 'T{i + 1}' (must be sequential)")
            if "status" in tc:
                errors.extend(_enum(tc["status"], VALID_TEST_STATUSES, f"{prefix}.status"))

    appr = record.get("approval")
    if isinstance(appr, dict):
        errors.extend(_required(appr, ["approved", "test_coverage_status"], "approval"))
        if appr.get("approved") is True:
            if not appr.get("approved_by"):
                errors.append("approval.approved_by is required when approval.approved is true")
            if not appr.get("approved_date"):
                errors.append("approval.approved_date is required when approval.approved is true")
        if "test_coverage_status" in appr:
            errors.extend(_enum(appr["test_coverage_status"], VALID_COVERAGE, "approval.test_coverage_status"))
    elif "approval" in record:
        errors.append("Field 'approval' must be an object")

    ctx = record.get("session_context")
    if isinstance(ctx, dict):
        errors.extend(_required(ctx, ["current_session"], "session_context"))
        cs = ctx.get("current_session")
        if isinstance(cs, dict):
            errors.extend(_required(cs, ["session_id", "platform", "model", "started"], "session_context.current_session"))
            if "platform" in cs:
                errors.extend(_enum(cs["platform"], VALID_PLATFORMS, "session_context.current_session.platform"))
            if "started" in cs:
                errors.extend(_iso(cs["started"], "session_context.current_session.started"))

    meta = record.get("metadata")
    if isinstance(meta, dict):
        errors.extend(_required(meta, ["project", "created_by", "last_modified_by", "last_modified"], "metadata"))
        if "last_modified" in meta:
            errors.extend(_iso(meta["last_modified"], "metadata.last_modified"))

    return errors

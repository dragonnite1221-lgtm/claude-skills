# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_validator_base import *  # noqa: F403,E402


VALID_STATUSES = ("planned", "in_progress", "blocked", "implemented", "tested", "deployed")
VALID_TRANSITIONS = {
    "planned":     ["in_progress", "blocked"],
    "in_progress": ["blocked", "implemented"],
    "blocked":     ["in_progress", "planned"],
    "implemented": ["tested", "in_progress"],
    "tested":      ["deployed", "in_progress"],
    "deployed":    ["in_progress"],
}
VALID_SCOPES = ("feature", "bugfix", "refactor", "infrastructure", "documentation", "hotfix", "enhancement")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
VALID_FILE_ACTIONS = ("created", "modified", "deleted", "renamed")
VALID_TEST_STATUSES = ("pending", "pass", "fail", "skip", "blocked")
VALID_EVIDENCE_TYPES = ("log_snippet", "screenshot", "file_reference", "command_output")
VALID_FIELD_CHANGE_ACTIONS = ("set", "changed", "added", "removed")
VALID_PLATFORMS = ("claude_code", "claude_web", "api", "other")
VALID_COVERAGE = ("none", "partial", "full")
VALID_FILE_IN_PROGRESS_STATES = ("editing", "needs_review", "partially_done", "ready")
TC_ID_PATTERN = re.compile(r"^TC-\d{3}-\d{2}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")
SUB_TC_PATTERN = re.compile(r"^TC-\d{3}\.[A-Z](\.\d+)?$")
REVISION_ID_PATTERN = re.compile(r"^R(\d+)$")
TEST_ID_PATTERN = re.compile(r"^T(\d+)$")
def _enum(value, valid, name):
    if value not in valid:
        return [f"Field '{name}' has invalid value '{value}'. Must be one of: {', '.join(str(v) for v in valid)}"]
    return []
def _string(value, name, min_length=0, max_length=None):
    errors = []
    if not isinstance(value, str):
        return [f"Field '{name}' must be a string, got {type(value).__name__}"]
    if len(value) < min_length:
        errors.append(f"Field '{name}' must be at least {min_length} characters, got {len(value)}")
    if max_length is not None and len(value) > max_length:
        errors.append(f"Field '{name}' must be at most {max_length} characters, got {len(value)}")
    return errors
def _iso(value, name):
    if value is None:
        return []
    if not isinstance(value, str):
        return [f"Field '{name}' must be an ISO 8601 datetime string"]
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return [f"Field '{name}' is not a valid ISO 8601 datetime: '{value}'"]
    return []
def _required(record, fields, prefix=""):
    errors = []
    for f in fields:
        if f not in record:
            path = f"{prefix}.{f}" if prefix else f
            errors.append(f"Missing required field: '{path}'")
    return errors
def validate_tc_id(tc_id):
    """Validate a TC identifier."""
    if not isinstance(tc_id, str):
        return [f"tc_id must be a string, got {type(tc_id).__name__}"]
    if not TC_ID_PATTERN.match(tc_id):
        return [f"tc_id '{tc_id}' does not match pattern TC-NNN-MM-DD-YY-slug"]
    return []
def validate_state_transition(current, new):
    """Validate a state machine transition. Same-status is a no-op."""
    errors = []
    if current not in VALID_STATUSES:
        errors.append(f"Current status '{current}' is invalid")
    if new not in VALID_STATUSES:
        errors.append(f"New status '{new}' is invalid")
    if errors:
        return errors
    if current == new:
        return []
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        return [f"Invalid transition '{current}' -> '{new}'. Allowed from '{current}': {', '.join(allowed) or 'none'}"]
    return []

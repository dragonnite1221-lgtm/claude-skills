# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_log_analyzer_base import *  # noqa: F403,E402


def load_logs(path):
    """Load audit log entries from file. Supports JSON lines and JSON array."""
    entries = []
    try:
        with open(path, "r") as f:
            content = f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: Log file not found: {path}", file=sys.stderr)
        sys.exit(1)

    if not content:
        return entries

    # Try JSON array first
    if content.startswith("["):
        try:
            entries = json.loads(content)
            return entries
        except json.JSONDecodeError:
            pass

    # Try JSON lines
    for i, line in enumerate(content.split("\n"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"WARNING: Skipping malformed line {i}", file=sys.stderr)

    return entries
def extract_fields(entry):
    """Extract normalized fields from a log entry."""
    timestamp_raw = entry.get("timestamp", entry.get("time", ""))
    ts = None
    if timestamp_raw:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
            try:
                ts = datetime.strptime(timestamp_raw.replace("+00:00", "Z").rstrip("Z") + "Z", fmt.rstrip("Z") + "Z") if "Z" not in fmt else datetime.strptime(timestamp_raw, fmt)
                break
            except (ValueError, TypeError):
                continue
        if ts is None:
            # Fallback: try basic parse
            try:
                ts = datetime.fromisoformat(timestamp_raw.replace("Z", "+00:00").replace("+00:00", ""))
            except (ValueError, TypeError):
                pass

    auth = entry.get("auth", {})
    request = entry.get("request", {})
    response = entry.get("response", {})

    return {
        "timestamp": ts,
        "hour": ts.hour if ts else None,
        "identity": auth.get("display_name", auth.get("entity_id", "unknown")),
        "path": request.get("path", entry.get("path", "unknown")),
        "operation": request.get("operation", entry.get("operation", "unknown")),
        "status_code": response.get("status_code", entry.get("status_code")),
        "remote_address": entry.get("remote_address", entry.get("source_address", "unknown")),
        "entry_type": entry.get("type", "unknown"),
    }

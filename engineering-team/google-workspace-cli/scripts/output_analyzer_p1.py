# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from output_analyzer_base import *  # noqa: F403,E402


DEMO_DATA = [
    {"id": "1", "name": "Q1 Report.pdf", "mimeType": "application/pdf", "size": "245760",
     "modifiedTime": "2026-03-10T14:30:00Z", "shared": True, "owners": [{"displayName": "Alice"}]},
    {"id": "2", "name": "Budget 2026.xlsx", "mimeType": "application/vnd.google-apps.spreadsheet",
     "size": "0", "modifiedTime": "2026-03-09T09:15:00Z", "shared": True,
     "owners": [{"displayName": "Bob"}]},
    {"id": "3", "name": "Meeting Notes.docx", "mimeType": "application/vnd.google-apps.document",
     "size": "0", "modifiedTime": "2026-03-08T16:00:00Z", "shared": False,
     "owners": [{"displayName": "Alice"}]},
    {"id": "4", "name": "Logo.png", "mimeType": "image/png", "size": "102400",
     "modifiedTime": "2026-03-07T11:00:00Z", "shared": False,
     "owners": [{"displayName": "Charlie"}]},
    {"id": "5", "name": "Presentation.pptx", "mimeType": "application/vnd.google-apps.presentation",
     "size": "0", "modifiedTime": "2026-03-06T10:00:00Z", "shared": True,
     "owners": [{"displayName": "Alice"}]},
    {"id": "6", "name": "Invoice-001.pdf", "mimeType": "application/pdf", "size": "89000",
     "modifiedTime": "2026-03-05T08:30:00Z", "shared": False,
     "owners": [{"displayName": "Bob"}]},
    {"id": "7", "name": "Project Plan.xlsx", "mimeType": "application/vnd.google-apps.spreadsheet",
     "size": "0", "modifiedTime": "2026-03-04T13:45:00Z", "shared": True,
     "owners": [{"displayName": "Charlie"}]},
    {"id": "8", "name": "Contract Draft.docx", "mimeType": "application/vnd.google-apps.document",
     "size": "0", "modifiedTime": "2026-03-03T09:00:00Z", "shared": False,
     "owners": [{"displayName": "Alice"}]},
]
def read_input(input_file: Optional[str]) -> List[Dict[str, Any]]:
    """Read JSON array or NDJSON from file or stdin."""
    if input_file:
        with open(input_file, "r") as f:
            text = f.read().strip()
    else:
        if sys.stdin.isatty():
            return []
        text = sys.stdin.read().strip()

    if not text:
        return []

    # Try JSON array first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Some gws commands wrap results in a key
            for key in ("files", "messages", "events", "items", "results",
                        "spreadsheets", "spaces", "tasks", "users", "groups"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            return [data]
    except json.JSONDecodeError:
        pass

    # Try NDJSON
    records = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records
def get_nested(obj: Dict, path: str) -> Any:
    """Get a nested value by dot-separated path."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if idx < len(current) else None
        else:
            return None
        if current is None:
            return None
    return current
def apply_filter(records: List[Dict], filter_expr: str) -> List[Dict]:
    """Filter records by field=value expression."""
    if "=" not in filter_expr:
        return records
    field_path, value = filter_expr.split("=", 1)
    result = []
    for rec in records:
        rec_val = get_nested(rec, field_path)
        if rec_val is None:
            continue
        rec_str = str(rec_val).lower()
        if rec_str == value.lower() or value.lower() in rec_str:
            result.append(rec)
    return result
def apply_select(records: List[Dict], fields: str) -> List[Dict]:
    """Project specific fields from records."""
    field_list = [f.strip() for f in fields.split(",")]
    result = []
    for rec in records:
        projected = {}
        for f in field_list:
            projected[f] = get_nested(rec, f)
        result.append(projected)
    return result
def apply_sort(records: List[Dict], sort_field: str, reverse: bool = False) -> List[Dict]:
    """Sort records by a field."""
    def sort_key(rec):
        val = get_nested(rec, sort_field)
        if val is None:
            return ""
        if isinstance(val, (int, float)):
            return val
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val).lower()
    return sorted(records, key=sort_key, reverse=reverse)
def apply_group_by(records: List[Dict], field: str) -> Dict[str, int]:
    """Group records by a field and count."""
    groups: Dict[str, int] = {}
    for rec in records:
        val = get_nested(rec, field)
        key = str(val) if val is not None else "(null)"
        groups[key] = groups.get(key, 0) + 1
    return dict(sorted(groups.items(), key=lambda x: x[1], reverse=True))

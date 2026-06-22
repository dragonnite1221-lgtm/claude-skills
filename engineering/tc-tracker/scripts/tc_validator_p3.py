# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tc_validator_base import *  # noqa: F403,E402
# fmt: off
from tc_validator_p1 import VALID_PRIORITIES, VALID_SCOPES, VALID_STATUSES, _enum, _required  # noqa: E402,E501
from tc_validator_p2 import validate_tc_record  # noqa: E402,E501
# fmt: on


def validate_registry(registry):
    """Validate a TC registry dict."""
    errors = []
    if not isinstance(registry, dict):
        return [f"Registry must be an object, got {type(registry).__name__}"]
    errors.extend(_required(registry, ["project_name", "created", "updated", "next_tc_number", "records", "statistics"]))
    if "next_tc_number" in registry:
        v = registry["next_tc_number"]
        if not isinstance(v, int) or v < 1:
            errors.append(f"next_tc_number must be a positive integer, got {v}")
    if isinstance(registry.get("records"), list):
        for i, rec in enumerate(registry["records"]):
            prefix = f"records[{i}]"
            if not isinstance(rec, dict):
                errors.append(f"{prefix} must be an object")
                continue
            errors.extend(_required(rec, ["tc_id", "title", "status", "scope", "priority", "created", "updated", "path"], prefix))
            if "status" in rec:
                errors.extend(_enum(rec["status"], VALID_STATUSES, f"{prefix}.status"))
            if "scope" in rec:
                errors.extend(_enum(rec["scope"], VALID_SCOPES, f"{prefix}.scope"))
            if "priority" in rec:
                errors.extend(_enum(rec["priority"], VALID_PRIORITIES, f"{prefix}.priority"))
    return errors
def slugify(text):
    """Convert text to a kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
def compute_registry_statistics(records):
    """Recompute registry statistics from the records array."""
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
def main():
    parser = argparse.ArgumentParser(description="Validate a TC record or registry.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record", help="Path to tc_record.json")
    group.add_argument("--registry", help="Path to tc_registry.json")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    target = args.record or args.registry
    path = Path(target)
    if not path.exists():
        msg = f"File not found: {path}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON in {path}: {e}"
        print(json.dumps({"status": "error", "error": msg}) if args.json else f"ERROR: {msg}")
        return 2

    errors = validate_registry(data) if args.registry else validate_tc_record(data)

    if args.json:
        result = {
            "status": "valid" if not errors else "invalid",
            "file": str(path),
            "kind": "registry" if args.registry else "record",
            "error_count": len(errors),
            "errors": errors,
        }
        print(json.dumps(result, indent=2))
    else:
        if errors:
            print(f"VALIDATION ERRORS ({len(errors)}):")
            for i, err in enumerate(errors, 1):
                print(f"  {i}. {err}")
        else:
            print("VALID")

    return 1 if errors else 0

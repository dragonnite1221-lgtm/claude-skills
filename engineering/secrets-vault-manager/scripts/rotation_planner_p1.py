# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rotation_planner_base import *  # noqa: F403,E402


POLICY_DAYS = {
    "30d": 30,
    "60d": 60,
    "90d": 90,
}
TYPE_DEFAULTS = {
    "database": 30,
    "api-key": 90,
    "tls-certificate": 60,
    "ssh-key": 90,
    "service-token": 1,
    "encryption-key": 90,
    "oauth-secret": 90,
    "password": 30,
}
URGENCY_THRESHOLDS = {
    "critical": 0,    # Already overdue
    "high": 7,         # Due within 7 days
    "medium": 14,      # Due within 14 days
    "low": 30,         # Due within 30 days
}
def load_inventory(path):
    """Load and validate secret inventory from JSON file."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Inventory file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("ERROR: Inventory must be a JSON array of secret objects", file=sys.stderr)
        sys.exit(1)

    validated = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"WARNING: Skipping entry {i} — not an object", file=sys.stderr)
            continue

        name = entry.get("name", f"unnamed-{i}")
        secret_type = entry.get("type", "unknown")
        last_rotated = entry.get("last_rotated")

        if not last_rotated:
            print(f"WARNING: '{name}' has no last_rotated date — marking as overdue", file=sys.stderr)
            last_rotated_dt = None
        else:
            try:
                last_rotated_dt = datetime.strptime(last_rotated, "%Y-%m-%d")
            except ValueError:
                print(f"WARNING: '{name}' has invalid date '{last_rotated}' — marking as overdue", file=sys.stderr)
                last_rotated_dt = None

        validated.append({
            "name": name,
            "type": secret_type,
            "store": entry.get("store", "unknown"),
            "last_rotated": last_rotated_dt,
            "owner": entry.get("owner", "unassigned"),
            "environment": entry.get("environment", "unknown"),
        })

    return validated
def compute_schedule(inventory, policy_days):
    """Compute rotation schedule for each secret."""
    now = datetime.now()
    schedule = []

    for secret in inventory:
        # Determine rotation interval
        type_default = TYPE_DEFAULTS.get(secret["type"], 90)
        rotation_interval = min(policy_days, type_default)

        if secret["last_rotated"] is None:
            days_since = 999
            next_rotation = now  # Immediate
            days_until = -999
        else:
            days_since = (now - secret["last_rotated"]).days
            next_rotation = secret["last_rotated"] + timedelta(days=rotation_interval)
            days_until = (next_rotation - now).days

        # Classify urgency
        if days_until <= URGENCY_THRESHOLDS["critical"]:
            urgency = "CRITICAL"
        elif days_until <= URGENCY_THRESHOLDS["high"]:
            urgency = "HIGH"
        elif days_until <= URGENCY_THRESHOLDS["medium"]:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        schedule.append({
            "name": secret["name"],
            "type": secret["type"],
            "store": secret["store"],
            "owner": secret["owner"],
            "environment": secret["environment"],
            "last_rotated": secret["last_rotated"].strftime("%Y-%m-%d") if secret["last_rotated"] else "NEVER",
            "rotation_interval_days": rotation_interval,
            "next_rotation": next_rotation.strftime("%Y-%m-%d"),
            "days_until_due": days_until,
            "days_since_rotation": days_since,
            "urgency": urgency,
        })

    # Sort by urgency (critical first), then by days until due
    urgency_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    schedule.sort(key=lambda x: (urgency_order.get(x["urgency"], 4), x["days_until_due"]))

    return schedule

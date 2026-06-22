# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from evidence_tracker_base import *  # noqa: F403,E402


EVIDENCE_STATUSES = {
    "collected": "Evidence gathered and verified",
    "pending": "Evidence identified but not yet collected",
    "overdue": "Evidence past its collection deadline",
    "not_started": "No evidence collection initiated",
    "not_applicable": "Control not applicable to the environment",
}
REQUIRED_FIELDS = ["control_id", "tsc_criteria", "description", "evidence_required"]
def load_matrix(filepath: str) -> List[Dict[str, Any]]:
    """Load a control matrix from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    # Accept both {"controls": [...]} and plain [...]
    if isinstance(data, dict) and "controls" in data:
        controls = data["controls"]
    elif isinstance(data, list):
        controls = data
    else:
        print(
            "Error: Expected JSON with 'controls' array or a plain array.",
            file=sys.stderr,
        )
        sys.exit(1)

    return controls
def classify_evidence_status(control: Dict[str, Any]) -> str:
    """Classify the evidence collection status for a control."""
    status = control.get("status", "Not Started").lower().strip()
    evidence_date = control.get("evidence_date", "")

    if status in ("not_applicable", "n/a", "not applicable"):
        return "not_applicable"
    if status in ("collected", "complete", "done"):
        return "collected"
    if status in ("pending", "in progress", "in_progress"):
        # Check if overdue
        if evidence_date:
            try:
                due = datetime.strptime(evidence_date, "%Y-%m-%d")
                if due < datetime.now():
                    return "overdue"
            except ValueError:
                pass
        return "pending"
    if status in ("overdue", "late"):
        return "overdue"

    return "not_started"
def generate_status_report(controls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate an evidence collection status report."""
    total = len(controls)
    status_counts = {s: 0 for s in EVIDENCE_STATUSES}
    by_category: Dict[str, Dict[str, int]] = {}
    issues: List[Dict[str, str]] = []

    for ctrl in controls:
        status = classify_evidence_status(ctrl)
        status_counts[status] = status_counts.get(status, 0) + 1

        category = ctrl.get("category", "Unknown")
        if category not in by_category:
            by_category[category] = {s: 0 for s in EVIDENCE_STATUSES}
        by_category[category][status] += 1

        # Flag issues
        if status == "overdue":
            issues.append(
                {
                    "control_id": ctrl.get("control_id", "N/A"),
                    "tsc_criteria": ctrl.get("tsc_criteria", "N/A"),
                    "description": ctrl.get("description", "N/A"),
                    "issue": "Evidence collection overdue",
                    "evidence_date": ctrl.get("evidence_date", "N/A"),
                }
            )
        elif status == "not_started":
            issues.append(
                {
                    "control_id": ctrl.get("control_id", "N/A"),
                    "tsc_criteria": ctrl.get("tsc_criteria", "N/A"),
                    "description": ctrl.get("description", "N/A"),
                    "issue": "Evidence collection not started",
                }
            )

        # Check for missing required fields
        missing = [f for f in REQUIRED_FIELDS if f not in ctrl or not ctrl[f]]
        if missing:
            issues.append(
                {
                    "control_id": ctrl.get("control_id", "N/A"),
                    "issue": f"Missing fields: {', '.join(missing)}",
                }
            )

    # Calculate readiness score
    applicable = total - status_counts.get("not_applicable", 0)
    collected = status_counts.get("collected", 0)
    readiness_pct = round((collected / applicable * 100), 1) if applicable > 0 else 0.0

    if readiness_pct >= 90:
        readiness_rating = "Audit Ready"
    elif readiness_pct >= 75:
        readiness_rating = "Minor Gaps"
    elif readiness_pct >= 50:
        readiness_rating = "Significant Gaps"
    else:
        readiness_rating = "Not Ready"

    return {
        "summary": {
            "total_controls": total,
            "status_breakdown": status_counts,
            "readiness_score": readiness_pct,
            "readiness_rating": readiness_rating,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
        },
        "by_category": by_category,
        "issues": issues,
    }

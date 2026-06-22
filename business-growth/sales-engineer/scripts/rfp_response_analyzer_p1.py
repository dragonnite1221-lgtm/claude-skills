# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rfp_response_analyzer_base import *  # noqa: F403,E402


COVERAGE_SCORES: dict[str, float] = {
    "full": 1.0,
    "partial": 0.5,
    "planned": 0.25,
    "gap": 0.0,
}
PRIORITY_WEIGHTS: dict[str, float] = {
    "must-have": 3.0,
    "should-have": 2.0,
    "nice-to-have": 1.0,
}
BID_THRESHOLD = 0.70
CONDITIONAL_THRESHOLD = 0.50
MAX_MUST_HAVE_GAPS_FOR_BID = 3
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def load_rfp_data(filepath: str) -> dict[str, Any]:
    """Load and validate RFP data from a JSON file.

    Args:
        filepath: Path to the JSON file containing RFP data.

    Returns:
        Parsed RFP data dictionary.

    Raises:
        SystemExit: If the file cannot be read or parsed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    if "requirements" not in data:
        print("Error: JSON must contain a 'requirements' array.", file=sys.stderr)
        sys.exit(1)

    return data
def analyze_requirement(req: dict[str, Any]) -> dict[str, Any]:
    """Analyze a single requirement and compute its score.

    Args:
        req: Requirement dictionary with category, priority, coverage_status, etc.

    Returns:
        Enriched requirement with computed score and weight.
    """
    coverage_status = req.get("coverage_status", "gap").lower()
    priority = req.get("priority", "nice-to-have").lower()

    coverage_score = COVERAGE_SCORES.get(coverage_status, 0.0)
    weight = PRIORITY_WEIGHTS.get(priority, 1.0)
    weighted_score = coverage_score * weight
    max_weighted = weight

    effort_hours = req.get("effort_hours", 0)

    result = {
        "id": req.get("id", "unknown"),
        "requirement": req.get("requirement", "Unnamed requirement"),
        "category": req.get("category", "Uncategorized"),
        "priority": priority,
        "coverage_status": coverage_status,
        "coverage_score": coverage_score,
        "weight": weight,
        "weighted_score": weighted_score,
        "max_weighted": max_weighted,
        "effort_hours": effort_hours,
        "notes": req.get("notes", ""),
        "mitigation": req.get("mitigation", ""),
    }

    return result
def generate_gap_analysis(analyzed_reqs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate gap analysis for requirements not fully covered.

    Args:
        analyzed_reqs: List of analyzed requirement dictionaries.

    Returns:
        List of gap entries with mitigation strategies.
    """
    gaps = []
    for req in analyzed_reqs:
        if req["coverage_status"] in ("gap", "partial", "planned"):
            severity = "critical" if req["priority"] == "must-have" else (
                "high" if req["priority"] == "should-have" else "low"
            )

            mitigation = req["mitigation"]
            if not mitigation:
                if req["coverage_status"] == "partial":
                    mitigation = "Enhance existing capability to achieve full coverage"
                elif req["coverage_status"] == "planned":
                    mitigation = "Communicate roadmap timeline and interim workaround"
                else:
                    mitigation = "Evaluate build vs. partner vs. no-bid for this requirement"

            gaps.append({
                "id": req["id"],
                "requirement": req["requirement"],
                "category": req["category"],
                "priority": req["priority"],
                "coverage_status": req["coverage_status"],
                "severity": severity,
                "effort_hours": req["effort_hours"],
                "mitigation": mitigation,
            })

    # Sort by severity: critical > high > low
    severity_order = {"critical": 0, "high": 1, "low": 2}
    gaps.sort(key=lambda g: severity_order.get(g["severity"], 3))

    return gaps

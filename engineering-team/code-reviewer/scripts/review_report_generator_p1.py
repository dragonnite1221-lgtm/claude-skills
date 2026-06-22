# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_report_generator_base import *  # noqa: F403,E402


SEVERITY_WEIGHTS = {
    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
    "info": 10
}
VERDICT_THRESHOLDS = {
    "approve": {"max_critical": 0, "max_high": 0, "max_score": 100},
    "approve_with_suggestions": {"max_critical": 0, "max_high": 2, "max_score": 85},
    "request_changes": {"max_critical": 0, "max_high": 5, "max_score": 70},
    "block": {"max_critical": float("inf"), "max_high": float("inf"), "max_score": 0}
}
def load_json_file(filepath: str) -> Optional[Dict]:
    """Load JSON file if it exists."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
def run_pr_analyzer(repo_path: Path) -> Dict:
    """Run pr_analyzer.py and return results."""
    script_path = Path(__file__).parent / "pr_analyzer.py"
    if not script_path.exists():
        return {"status": "error", "message": "pr_analyzer.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(repo_path), "--json"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
def run_quality_checker(repo_path: Path) -> Dict:
    """Run code_quality_checker.py and return results."""
    script_path = Path(__file__).parent / "code_quality_checker.py"
    if not script_path.exists():
        return {"status": "error", "message": "code_quality_checker.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(repo_path), "--json"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
def calculate_review_score(pr_analysis: Dict, quality_analysis: Dict) -> int:
    """Calculate overall review score (0-100)."""
    score = 100

    # Deduct for PR risks
    if "risks" in pr_analysis:
        risks = pr_analysis["risks"]
        score -= len(risks.get("critical", [])) * 15
        score -= len(risks.get("high", [])) * 10
        score -= len(risks.get("medium", [])) * 5
        score -= len(risks.get("low", [])) * 2

    # Deduct for code quality issues
    if "issues" in quality_analysis:
        issues = quality_analysis["issues"]
        score -= len([i for i in issues if i.get("severity") == "critical"]) * 12
        score -= len([i for i in issues if i.get("severity") == "high"]) * 8
        score -= len([i for i in issues if i.get("severity") == "medium"]) * 4
        score -= len([i for i in issues if i.get("severity") == "low"]) * 1

    # Deduct for complexity
    if "summary" in pr_analysis:
        complexity = pr_analysis["summary"].get("complexity_score", 0)
        if complexity > 7:
            score -= 10
        elif complexity > 5:
            score -= 5

    return max(0, min(100, score))
def determine_verdict(score: int, critical_count: int, high_count: int) -> Tuple[str, str]:
    """Determine review verdict based on score and issue counts."""
    if critical_count > 0:
        return "block", "Critical issues must be resolved before merge"

    if score >= 90 and high_count == 0:
        return "approve", "Code meets quality standards"

    if score >= 75 and high_count <= 2:
        return "approve_with_suggestions", "Minor improvements recommended"

    if score >= 50:
        return "request_changes", "Several issues need to be addressed"

    return "block", "Significant issues prevent approval"

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_checker_base import *  # noqa: F403,E402
# fmt: off
from code_quality_checker_p1 import THRESHOLDS, count_lines, detect_language, find_functions, read_file_content  # noqa: E402,E501
from code_quality_checker_p2 import check_code_smells, find_classes  # noqa: E402,E501
# fmt: on


def check_solid_violations(content: str) -> List[Dict]:
    """Check for potential SOLID principle violations."""
    violations = []

    # OCP: Type checking instead of polymorphism
    type_checks = len(re.findall(r"isinstance\(|type\(.*\)\s*==|typeof\s+\w+\s*===", content))
    if type_checks > 2:
        violations.append({
            "principle": "OCP",
            "name": "Open/Closed Principle",
            "severity": "medium",
            "message": f"Found {type_checks} type checks - consider using polymorphism"
        })

    # LSP/ISP: NotImplementedError
    not_impl = len(re.findall(r"raise\s+NotImplementedError|not\s+implemented", content, re.IGNORECASE))
    if not_impl:
        violations.append({
            "principle": "LSP/ISP",
            "name": "Liskov/Interface Segregation",
            "severity": "low",
            "message": f"Found {not_impl} unimplemented methods - may indicate oversized interface"
        })

    # DIP: Too many direct imports
    imports = len(re.findall(r"^(?:import|from)\s+", content, re.MULTILINE))
    if imports > THRESHOLDS["max_imports"]:
        violations.append({
            "principle": "DIP",
            "name": "Dependency Inversion Principle",
            "severity": "low",
            "message": f"File has {imports} imports - consider dependency injection"
        })

    return violations
def calculate_quality_score(
    line_metrics: Dict,
    functions: List[Dict],
    classes: List[Dict],
    smells: List[Dict],
    violations: List[Dict]
) -> int:
    """Calculate overall quality score (0-100)."""
    score = 100

    # Deduct for code smells
    for smell in smells:
        if smell["severity"] == "high":
            score -= 10
        elif smell["severity"] == "medium":
            score -= 5
        elif smell["severity"] == "low":
            score -= 2

    # Deduct for SOLID violations
    for violation in violations:
        if violation["severity"] == "high":
            score -= 8
        elif violation["severity"] == "medium":
            score -= 4
        elif violation["severity"] == "low":
            score -= 2

    # Bonus for good comment ratio (10-30%)
    if line_metrics["total"] > 0:
        comment_ratio = line_metrics["comment"] / line_metrics["total"]
        if 0.1 <= comment_ratio <= 0.3:
            score += 5

    # Bonus for reasonable function sizes
    if functions:
        avg_lines = sum(f["lines"] for f in functions) / len(functions)
        if avg_lines < 30:
            score += 5

    return max(0, min(100, score))
def get_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
def analyze_file(filepath: Path) -> Dict:
    """Analyze a single file for code quality."""
    language = detect_language(filepath)
    if not language:
        return {"error": f"Unsupported file type: {filepath.suffix}"}

    content = read_file_content(filepath)
    if not content:
        return {"error": f"Could not read file: {filepath}"}

    line_metrics = count_lines(content)
    functions = find_functions(content, language)
    classes = find_classes(content, language)
    smells = check_code_smells(content, functions, classes)
    violations = check_solid_violations(content)
    score = calculate_quality_score(line_metrics, functions, classes, smells, violations)

    return {
        "file": str(filepath),
        "language": language,
        "metrics": {
            "lines": line_metrics,
            "functions": len(functions),
            "classes": len(classes),
            "avg_complexity": round(sum(f["complexity"] for f in functions) / max(1, len(functions)), 1)
        },
        "quality_score": score,
        "grade": get_grade(score),
        "smells": smells,
        "solid_violations": violations,
        "function_details": functions[:10],
        "class_details": classes[:10]
    }

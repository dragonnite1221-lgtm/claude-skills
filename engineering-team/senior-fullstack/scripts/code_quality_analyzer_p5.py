# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402
# fmt: off
from code_quality_analyzer_p1 import ALL_CODE_EXTENSIONS, CODE_SMELL_PATTERNS, count_lines, should_skip  # noqa: E402,E501
from code_quality_analyzer_p2 import analyze_dependencies, analyze_security, calculate_complexity  # noqa: E402,E501
from code_quality_analyzer_p3 import analyze_documentation, analyze_test_coverage  # noqa: E402,E501
from code_quality_analyzer_p4 import generate_recommendations  # noqa: E402,E501
# fmt: on


def analyze_project(project_path: Path) -> Dict:
    """Perform full project analysis."""
    results = {
        "summary": {
            "files_analyzed": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0
        },
        "languages": defaultdict(lambda: {"files": 0, "lines": 0}),
        "security": {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        },
        "complexity": {
            "high_complexity_files": [],
            "average_complexity": 0
        },
        "code_smells": [],
        "dependencies": {},
        "tests": {},
        "documentation": {},
        "overall_score": 100
    }

    complexity_scores = []
    security_issues = []

    # Analyze source files
    for filepath in project_path.rglob("*"):
        if should_skip(filepath) or not filepath.is_file():
            continue

        if filepath.suffix not in ALL_CODE_EXTENSIONS:
            continue

        results["summary"]["files_analyzed"] += 1

        # Count lines
        total, code, comments = count_lines(filepath)
        results["summary"]["total_lines"] += total
        results["summary"]["code_lines"] += code
        results["summary"]["comment_lines"] += comments

        # Track by language
        lang = "typescript" if filepath.suffix in {".ts", ".tsx"} else \
               "javascript" if filepath.suffix in {".js", ".jsx"} else \
               "python" if filepath.suffix == ".py" else \
               "go" if filepath.suffix == ".go" else "other"
        results["languages"][lang]["files"] += 1
        results["languages"][lang]["lines"] += code

        # Read file content
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        # Complexity analysis
        complexity = calculate_complexity(content, lang)
        complexity_scores.append(complexity["cyclomatic"])
        if complexity["rating"] == "high":
            results["complexity"]["high_complexity_files"].append({
                "file": str(filepath.relative_to(project_path)),
                "complexity": complexity["cyclomatic"],
                "nesting": complexity["max_nesting"]
            })

        # Security analysis
        issues = analyze_security(filepath.relative_to(project_path), content)
        security_issues.extend(issues)

        # Code smell: large file
        if total > CODE_SMELL_PATTERNS["large_file"]["threshold"]:
            results["code_smells"].append({
                "file": str(filepath.relative_to(project_path)),
                "type": "large_file",
                "details": f"{total} lines (threshold: {CODE_SMELL_PATTERNS['large_file']['threshold']})"
            })

    # Categorize security issues
    for issue in security_issues:
        severity = issue["severity"]
        results["security"][severity].append(issue)

    # Calculate average complexity
    if complexity_scores:
        results["complexity"]["average_complexity"] = round(
            sum(complexity_scores) / len(complexity_scores), 1
        )

    # Dependency analysis
    results["dependencies"] = analyze_dependencies(project_path)

    # Test coverage analysis
    results["tests"] = analyze_test_coverage(project_path)

    # Documentation analysis
    results["documentation"] = analyze_documentation(project_path)

    # Calculate overall score
    score = 100

    # Deduct for security issues
    score -= len(results["security"]["critical"]) * 15
    score -= len(results["security"]["high"]) * 10
    score -= len(results["security"]["medium"]) * 5
    score -= len(results["security"]["low"]) * 2

    # Deduct for high complexity
    score -= len(results["complexity"]["high_complexity_files"]) * 3

    # Deduct for code smells
    score -= len(results["code_smells"]) * 2

    # Deduct for vulnerable dependencies
    score -= len(results["dependencies"].get("vulnerable", [])) * 10

    # Deduct for poor test coverage
    if results["tests"].get("estimated_coverage", 0) < 50:
        score -= 15
    elif results["tests"].get("estimated_coverage", 0) < 70:
        score -= 5

    # Deduct for missing documentation
    doc_score = results["documentation"].get("score", 0)
    if doc_score < 50:
        score -= 10
    elif doc_score < 75:
        score -= 5

    results["overall_score"] = max(0, min(100, score))
    results["grade"] = (
        "A" if score >= 90 else
        "B" if score >= 80 else
        "C" if score >= 70 else
        "D" if score >= 60 else "F"
    )

    # Generate recommendations
    results["recommendations"] = generate_recommendations(results)

    # Convert defaultdict to regular dict for JSON serialization
    results["languages"] = dict(results["languages"])

    return results

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_checker_base import *  # noqa: F403,E402
# fmt: off
from code_quality_checker_p1 import THRESHOLDS  # noqa: E402,E501
# fmt: on


def find_classes(content: str, language: str) -> List[Dict]:
    """Find class definitions and their metrics."""
    classes = []

    patterns = {
        "python": r"class\s+(\w+)",
        "typescript": r"class\s+(\w+)",
        "javascript": r"class\s+(\w+)",
        "go": r"type\s+(\w+)\s+struct",
        "swift": r"class\s+(\w+)",
        "kotlin": r"class\s+(\w+)"
    }

    pattern = patterns.get(language, patterns["python"])
    matches = re.finditer(pattern, content)

    for match in matches:
        name = match.group(1)

        start_pos = match.end()
        remaining = content[start_pos:]

        next_class = re.search(pattern, remaining)
        if next_class:
            class_body = remaining[:next_class.start()]
        else:
            class_body = remaining

        # Count methods
        method_patterns = {
            "python": r"def\s+\w+\s*\(",
            "typescript": r"(?:public|private|protected)?\s*\w+\s*\([^)]*\)\s*[:{]",
            "javascript": r"\w+\s*\([^)]*\)\s*\{",
            "go": r"func\s+\(",
            "swift": r"func\s+\w+",
            "kotlin": r"fun\s+\w+"
        }
        method_pattern = method_patterns.get(language, method_patterns["python"])
        methods = len(re.findall(method_pattern, class_body))

        classes.append({
            "name": name,
            "methods": methods,
            "lines": len(class_body.split("\n"))
        })

    return classes
def check_code_smells(content: str, functions: List[Dict], classes: List[Dict]) -> List[Dict]:
    """Check for code smells in the content."""
    smells = []

    # Long functions
    for func in functions:
        if func["lines"] > THRESHOLDS["long_function_lines"]:
            smells.append({
                "type": "long_function",
                "severity": "medium",
                "message": f"Function '{func['name']}' has {func['lines']} lines (max: {THRESHOLDS['long_function_lines']})",
                "location": func["name"]
            })

    # Too many parameters
    for func in functions:
        if func["parameters"] > THRESHOLDS["too_many_parameters"]:
            smells.append({
                "type": "too_many_parameters",
                "severity": "low",
                "message": f"Function '{func['name']}' has {func['parameters']} parameters (max: {THRESHOLDS['too_many_parameters']})",
                "location": func["name"]
            })

    # High complexity
    for func in functions:
        if func["complexity"] > THRESHOLDS["high_complexity"]:
            severity = "high" if func["complexity"] > 20 else "medium"
            smells.append({
                "type": "high_complexity",
                "severity": severity,
                "message": f"Function '{func['name']}' has complexity {func['complexity']} (max: {THRESHOLDS['high_complexity']})",
                "location": func["name"]
            })

    # God classes
    for cls in classes:
        if cls["methods"] > THRESHOLDS["god_class_methods"]:
            smells.append({
                "type": "god_class",
                "severity": "high",
                "message": f"Class '{cls['name']}' has {cls['methods']} methods (max: {THRESHOLDS['god_class_methods']})",
                "location": cls["name"]
            })

    # Magic numbers
    magic_pattern = r"\b(?<![.\"\'])\d{3,}\b(?!\.\d)"
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith(("#", "//", "import", "from")):
            continue
        matches = re.findall(magic_pattern, line)
        for match in matches[:1]:  # One per line
            smells.append({
                "type": "magic_number",
                "severity": "low",
                "message": f"Magic number {match} should be a named constant",
                "location": f"line {i}"
            })

    # Commented code patterns
    commented_code_pattern = r"^\s*[#//]+\s*(if|for|while|def|function|class|const|let|var)\s"
    for i, line in enumerate(content.split("\n"), 1):
        if re.match(commented_code_pattern, line, re.IGNORECASE):
            smells.append({
                "type": "commented_code",
                "severity": "low",
                "message": "Commented-out code should be removed",
                "location": f"line {i}"
            })

    return smells

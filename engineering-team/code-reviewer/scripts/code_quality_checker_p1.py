# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_checker_base import *  # noqa: F403,E402


LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "typescript": [".ts", ".tsx"],
    "javascript": [".js", ".jsx", ".mjs"],
    "go": [".go"],
    "swift": [".swift"],
    "kotlin": [".kt", ".kts"]
}
THRESHOLDS = {
    "long_function_lines": 50,
    "too_many_parameters": 5,
    "high_complexity": 10,
    "god_class_methods": 20,
    "max_imports": 15
}
def get_file_extension(filepath: Path) -> str:
    """Get file extension."""
    return filepath.suffix.lower()
def detect_language(filepath: Path) -> Optional[str]:
    """Detect programming language from file extension."""
    ext = get_file_extension(filepath)
    for lang, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return lang
    return None
def read_file_content(filepath: Path) -> str:
    """Read file content safely."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""
def calculate_cyclomatic_complexity(content: str) -> int:
    """
    Estimate cyclomatic complexity based on control flow keywords.
    """
    complexity = 1  # Base complexity

    # Control flow patterns that increase complexity
    patterns = [
        r"\bif\b",
        r"\belif\b",
        r"\belse\b",
        r"\bfor\b",
        r"\bwhile\b",
        r"\bcase\b",
        r"\bcatch\b",
        r"\bexcept\b",
        r"\band\b",
        r"\bor\b",
        r"\|\|",
        r"&&"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        complexity += len(matches)

    return complexity
def count_lines(content: str) -> Dict[str, int]:
    """Count different types of lines in code."""
    lines = content.split("\n")
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comment = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            comment += 1
        elif stripped.startswith("/*") or stripped.startswith("'''") or stripped.startswith('"""'):
            comment += 1

    code = total - blank - comment

    return {
        "total": total,
        "code": code,
        "blank": blank,
        "comment": comment
    }
def find_functions(content: str, language: str) -> List[Dict]:
    """Find function definitions and their metrics."""
    functions = []

    # Language-specific function patterns
    patterns = {
        "python": r"def\s+(\w+)\s*\(([^)]*)\)",
        "typescript": r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)",
        "javascript": r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)",
        "go": r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)",
        "swift": r"func\s+(\w+)\s*\(([^)]*)\)",
        "kotlin": r"fun\s+(\w+)\s*\(([^)]*)\)"
    }

    pattern = patterns.get(language, patterns["python"])
    matches = re.finditer(pattern, content, re.MULTILINE)

    for match in matches:
        name = next((g for g in match.groups() if g), "anonymous")
        params_str = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""

        # Count parameters
        params = [p.strip() for p in params_str.split(",") if p.strip()]
        param_count = len(params)

        # Estimate function length
        start_pos = match.end()
        remaining = content[start_pos:]

        next_func = re.search(pattern, remaining)
        if next_func:
            func_body = remaining[:next_func.start()]
        else:
            func_body = remaining[:min(2000, len(remaining))]

        line_count = len(func_body.split("\n"))
        complexity = calculate_cyclomatic_complexity(func_body)

        functions.append({
            "name": name,
            "parameters": param_count,
            "lines": line_count,
            "complexity": complexity
        })

    return functions

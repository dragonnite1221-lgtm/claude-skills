# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402


FRONTEND_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte"}
BACKEND_EXTENSIONS = {".py", ".go", ".java", ".rb", ".php", ".cs"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".env"}
ALL_CODE_EXTENSIONS = FRONTEND_EXTENSIONS | BACKEND_EXTENSIONS
SKIP_DIRS = {"node_modules", "vendor", ".git", "__pycache__", "dist", "build",
             ".next", ".venv", "venv", "env", "coverage", ".pytest_cache"}
SECURITY_PATTERNS = {
    "hardcoded_secret": {
        "pattern": r"(?:password|secret|api_key|apikey|token|auth)[\s]*[=:][\s]*['\"][^'\"]{8,}['\"]",
        "severity": "critical",
        "message": "Potential hardcoded secret detected"
    },
    "sql_injection": {
        "pattern": r"(?:execute|query|raw)\s*\(\s*[f'\"].*\{.*\}|%s|%d|\$\d",
        "severity": "high",
        "message": "Potential SQL injection vulnerability"
    },
    "xss_vulnerable": {
        "pattern": r"innerHTML\s*=|v-html",
        "severity": "medium",
        "message": "Potential XSS vulnerability - unescaped HTML rendering"
    },
    "unsafe_react_html": {
        "pattern": r"__html",
        "severity": "medium",
        "message": "React unsafe HTML pattern detected - ensure content is sanitized"
    },
    "insecure_protocol": {
        "pattern": r"http://(?!localhost|127\.0\.0\.1)",
        "severity": "medium",
        "message": "Insecure HTTP protocol used"
    },
    "debug_code": {
        "pattern": r"console\.log|print\(|debugger|DEBUG\s*=\s*True",
        "severity": "low",
        "message": "Debug code should be removed in production"
    },
    "todo_fixme": {
        "pattern": r"(?:TODO|FIXME|HACK|XXX):",
        "severity": "info",
        "message": "Unresolved TODO/FIXME comment"
    }
}
CODE_SMELL_PATTERNS = {
    "long_function": {
        "description": "Function exceeds recommended length",
        "threshold": 50
    },
    "deep_nesting": {
        "description": "Excessive nesting depth",
        "threshold": 4
    },
    "large_file": {
        "description": "File exceeds recommended size",
        "threshold": 500
    },
    "magic_number": {
        "pattern": r"(?<![a-zA-Z_])\b(?:[2-9]\d{2,}|\d{4,})\b(?![a-zA-Z_])",
        "description": "Magic number should be named constant"
    }
}
KNOWN_VULNERABLE_DEPS = {
    "lodash": {"vulnerable_below": "4.17.21", "cve": "CVE-2021-23337"},
    "axios": {"vulnerable_below": "0.21.2", "cve": "CVE-2021-3749"},
    "minimist": {"vulnerable_below": "1.2.6", "cve": "CVE-2021-44906"},
    "jsonwebtoken": {"vulnerable_below": "9.0.0", "cve": "CVE-2022-23529"},
}
def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(skip in path.parts for skip in SKIP_DIRS)
def count_lines(filepath: Path) -> Tuple[int, int, int]:
    """Count total lines, code lines, and comment lines."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return 0, 0, 0

    total = len(lines)
    code = 0
    comments = 0
    in_block_comment = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Block comments
        if "/*" in stripped:
            in_block_comment = True
        if in_block_comment:
            comments += 1
            if "*/" in stripped:
                in_block_comment = False
            continue

        # Line comments
        if stripped.startswith(("//", "#", "--", "'")):
            comments += 1
        else:
            code += 1

    return total, code, comments

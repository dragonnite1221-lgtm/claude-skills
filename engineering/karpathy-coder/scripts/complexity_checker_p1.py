# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from complexity_checker_base import *  # noqa: F403,E402


THRESHOLDS = {
    "strict": {
        "max_cyclomatic": 5,
        "max_nesting": 3,
        "max_function_lines": 30,
        "max_imports": 10,
        "max_classes_per_100_lines": 2,
        "max_file_lines": 300,
    },
    "medium": {
        "max_cyclomatic": 8,
        "max_nesting": 4,
        "max_function_lines": 50,
        "max_imports": 15,
        "max_classes_per_100_lines": 3,
        "max_file_lines": 500,
    },
    "relaxed": {
        "max_cyclomatic": 12,
        "max_nesting": 5,
        "max_function_lines": 80,
        "max_imports": 25,
        "max_classes_per_100_lines": 5,
        "max_file_lines": 1000,
    },
}
BRANCH_KEYWORDS_PY = re.compile(
    r"^\s*(if |elif |for |while |except |with |and |or |case )", re.MULTILINE
)
BRANCH_KEYWORDS_TS = re.compile(
    r"^\s*(if\s*\(|else if|for\s*\(|while\s*\(|catch\s*\(|case |switch\s*\(|\?\?|&&|\|\|)",
    re.MULTILINE,
)
FUNC_DEF_PY = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)", re.MULTILINE)
FUNC_DEF_TS = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)|(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\()",
    re.MULTILINE,
)
CLASS_DEF_PY = re.compile(r"^\s*class\s+\w+", re.MULTILINE)
CLASS_DEF_TS = re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+\w+", re.MULTILINE)
IMPORT_PY = re.compile(r"^(?:import |from \S+ import )", re.MULTILINE)
IMPORT_TS = re.compile(r"^import\s+", re.MULTILINE)
ABC_PATTERN = re.compile(r"ABC|abstractmethod|Protocol|@abstract|Abstract\w+Base", re.MULTILINE)
INDENT_RE = re.compile(r"^( *)\S", re.MULTILINE)
def detect_lang(path):
    ext = path.suffix.lower()
    if ext in {".py"}:
        return "python"
    if ext in {".ts", ".tsx", ".js", ".jsx"}:
        return "typescript"
    return None
def count_branches(text, lang):
    pat = BRANCH_KEYWORDS_PY if lang == "python" else BRANCH_KEYWORDS_TS
    return len(pat.findall(text))
def extract_functions(text, lang):
    """Return list of (name, start_line, line_count)."""
    pat = FUNC_DEF_PY if lang == "python" else FUNC_DEF_TS
    lines = text.splitlines()
    funcs = []
    for m in pat.finditer(text):
        name = m.group(1) or (m.group(2) if m.lastindex and m.lastindex >= 2 else "anonymous")
        start = text[:m.start()].count("\n")
        # Estimate function length: count indented lines until next same-level def or end
        indent = len(m.group(0)) - len(m.group(0).lstrip())
        end = start + 1
        for i in range(start + 1, len(lines)):
            stripped = lines[i].rstrip()
            if not stripped:
                continue
            line_indent = len(stripped) - len(stripped.lstrip())
            if line_indent <= indent and stripped.lstrip() and not stripped.lstrip().startswith(("#", "//", "/*", "*")):
                if lang == "python" and (stripped.lstrip().startswith("def ") or stripped.lstrip().startswith("class ") or stripped.lstrip().startswith("async def ")):
                    break
                if lang == "typescript" and pat.match(stripped):
                    break
            end = i + 1
        funcs.append({"name": name, "start_line": start + 1, "lines": end - start})
    return funcs
def max_nesting(text, lang):
    """Return the maximum indentation depth in the file."""
    if lang == "python":
        unit = 4
    else:
        unit = 2
    depths = []
    for m in INDENT_RE.finditer(text):
        spaces = len(m.group(1))
        depths.append(spaces // unit if unit else 0)
    return max(depths) if depths else 0

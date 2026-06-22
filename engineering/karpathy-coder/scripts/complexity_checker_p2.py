# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from complexity_checker_base import *  # noqa: F403,E402
# fmt: off
from complexity_checker_p1 import ABC_PATTERN, CLASS_DEF_PY, CLASS_DEF_TS, IMPORT_PY, IMPORT_TS, count_branches, detect_lang, extract_functions, max_nesting  # noqa: E402,E501
# fmt: on


def analyze_file(path, thresholds):
    """Analyze a single file. Return dict with findings."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lang = detect_lang(path)
    if not lang:
        return None

    lines = text.splitlines()
    line_count = len(lines)
    findings = []

    # File length
    if line_count > thresholds["max_file_lines"]:
        findings.append({
            "rule": "file-length",
            "severity": "warn",
            "message": f"File is {line_count} lines (max {thresholds['max_file_lines']}). Consider splitting.",
        })

    # Import count
    imp_pat = IMPORT_PY if lang == "python" else IMPORT_TS
    import_count = len(imp_pat.findall(text))
    if import_count > thresholds["max_imports"]:
        findings.append({
            "rule": "import-count",
            "severity": "warn",
            "message": f"{import_count} imports (max {thresholds['max_imports']}). High coupling?",
        })

    # Class density
    cls_pat = CLASS_DEF_PY if lang == "python" else CLASS_DEF_TS
    class_count = len(cls_pat.findall(text))
    if line_count > 0:
        density = class_count / (line_count / 100)
        if density > thresholds["max_classes_per_100_lines"]:
            findings.append({
                "rule": "class-density",
                "severity": "warn",
                "message": f"{class_count} classes in {line_count} lines ({density:.1f} per 100). Premature abstraction?",
            })

    # Premature ABC/Protocol in small files
    if class_count > 0 and line_count < 200 and ABC_PATTERN.search(text):
        findings.append({
            "rule": "premature-abstraction",
            "severity": "warn",
            "message": "Abstract base class / Protocol in a file under 200 lines. Is this needed yet?",
        })

    # Nesting depth
    depth = max_nesting(text, lang)
    if depth > thresholds["max_nesting"]:
        findings.append({
            "rule": "nesting-depth",
            "severity": "warn",
            "message": f"Max nesting depth {depth} (max {thresholds['max_nesting']}). Extract or flatten.",
        })

    # Cyclomatic complexity (file-level)
    branches = count_branches(text, lang)
    funcs = extract_functions(text, lang)
    func_count = max(len(funcs), 1)
    avg_cyclomatic = branches / func_count
    if avg_cyclomatic > thresholds["max_cyclomatic"]:
        findings.append({
            "rule": "cyclomatic-complexity",
            "severity": "warn",
            "message": f"Average cyclomatic complexity {avg_cyclomatic:.1f} (max {thresholds['max_cyclomatic']}). Simplify branching.",
        })

    # Function length
    for f in funcs:
        if f["lines"] > thresholds["max_function_lines"]:
            findings.append({
                "rule": "function-length",
                "severity": "warn",
                "message": f"Function '{f['name']}' is {f['lines']} lines (max {thresholds['max_function_lines']}). Split it.",
                "line": f["start_line"],
            })

    score = max(0, 100 - len(findings) * 15)
    return {
        "file": str(path),
        "language": lang,
        "lines": line_count,
        "functions": len(funcs),
        "classes": class_count,
        "imports": import_count,
        "max_nesting": depth,
        "avg_cyclomatic": round(avg_cyclomatic, 1),
        "score": score,
        "findings": findings,
    }
def collect_files(target, extensions):
    target = Path(target)
    if target.is_file():
        return [target]
    files = []
    for ext in extensions:
        files.extend(target.rglob(f"*.{ext}"))
    # Exclude common non-source dirs
    skip = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
    return [f for f in files if not any(p in skip for p in f.parts)]

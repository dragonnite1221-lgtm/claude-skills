# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import AuditReport, Finding  # noqa: E402,E501
from skill_security_auditor_p4 import CODE_PATTERNS, PROMPT_INJECTION_PATTERNS  # noqa: E402,E501
from skill_security_auditor_p5 import JS_PATTERNS, SHELL_PATTERNS  # noqa: E402,E501
# fmt: on


def mask_python_noncode(content: str) -> str:
    """Blank out string and comment token text in Python source, preserving
    line/column offsets, so the pattern scanner sees only executable code.

    This removes the 'scanner flags scanner' false positives: a security tool's
    docstrings and pattern-definition string literals (e.g. the text
    "os.system(), os.popen() usage") are not executable calls and must not be
    flagged. A real `os.system(...)` call is a NAME token and survives masking,
    so genuine detections are preserved."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return content  # fall back to raw text on un-tokenizable input

    lines = content.split("\n")
    for tok in tokens:
        if tok.type not in (tokenize.STRING, tokenize.COMMENT) and \
                tok.type != getattr(tokenize, "FSTRING_MIDDLE", -1):
            continue
        (srow, scol), (erow, ecol) = tok.start, tok.end
        for row in range(srow, erow + 1):
            idx = row - 1
            if idx >= len(lines):
                continue
            line = lines[idx]
            start = scol if row == srow else 0
            end = ecol if row == erow else len(line)
            lines[idx] = line[:start] + " " * (end - start) + line[end:]
    return "\n".join(lines)
def scan_file_code(filepath: Path, report: AuditReport):
    """Scan a code file for dangerous patterns."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    ext = filepath.suffix.lower()
    original_lines = content.split("\n")
    # For Python, match against a version with string/comment text blanked so
    # only executable code is scanned; report the original line for context.
    scan_lines = mask_python_noncode(content).split("\n") if ext == ".py" else original_lines

    # Select pattern sets based on file type
    patterns = list(CODE_PATTERNS)
    if ext in {".sh", ".bash"}:
        patterns.extend(SHELL_PATTERNS)
    if ext in {".js", ".ts", ".mjs", ".cjs"}:
        patterns.extend(JS_PATTERNS)

    for i, (scan_line, orig_line) in enumerate(zip(scan_lines, original_lines), 1):
        stripped = scan_line.strip()
        # Skip comments
        if stripped.startswith("#") and ext in {".py", ".sh", ".bash"}:
            continue
        if stripped.startswith("//") and ext in {".js", ".ts", ".mjs", ".cjs"}:
            continue

        for pat in patterns:
            if re.search(pat["regex"], scan_line):
                report.findings.append(
                    Finding(
                        severity=pat["severity"],
                        category=pat["category"],
                        file=str(filepath),
                        line=i,
                        pattern=orig_line.strip()[:120],
                        risk=pat["risk"],
                        fix=pat["fix"],
                    )
                )
def scan_file_prompt_injection(filepath: Path, report: AuditReport):
    """Scan a markdown file for prompt injection patterns."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        for pat in PROMPT_INJECTION_PATTERNS:
            if re.search(pat["regex"], line):
                report.findings.append(
                    Finding(
                        severity=pat["severity"],
                        category=pat["category"],
                        file=str(filepath),
                        line=i,
                        pattern=line.strip()[:120],
                        risk=pat["risk"],
                        fix=pat["fix"],
                    )
                )

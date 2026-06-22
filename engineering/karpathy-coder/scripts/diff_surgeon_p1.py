# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from diff_surgeon_base import *  # noqa: F403,E402


COMMENT_ONLY = re.compile(r"^[+-]\s*(?:#|//|/\*|\*|<!--)")
WHITESPACE_ONLY = re.compile(r"^[+-]\s*$")
QUOTE_CHANGE = re.compile(r'^[+-]\s*.*["\'].*["\']')
DOCSTRING_ADD = re.compile(r'^[+]\s*"""')
IMPORT_LINE = re.compile(r"^[+]\s*(?:import |from \S+ import |const .* = require)")
TYPE_ANNOTATION = re.compile(r"^[+-].*:\s*(?:str|int|float|bool|list|dict|Optional|Union|Any|string|number|boolean)\b")
SEMICOLON_CHANGE = re.compile(r"^[+-].*;\s*$")
TRAILING_COMMA = re.compile(r"^[+-].*,\s*$")
def get_diff(args):
    """Get diff text from args."""
    if args.file:
        return Path(args.file).read_text(encoding="utf-8", errors="replace")
    diff_range = args.diff or "--staged"
    cmd = ["git", "diff", diff_range] if diff_range != "--staged" else ["git", "diff", "--staged"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"[error] git diff failed: {e}", file=sys.stderr)
        sys.exit(1)
def parse_hunks(diff_text):
    """Parse a unified diff into per-file hunks."""
    files = []
    current_file = None
    current_lines = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file:
                files.append({"file": current_file, "lines": current_lines})
            # Extract filename: diff --git a/path b/path
            parts = line.split(" b/")
            current_file = parts[-1] if len(parts) > 1 else "unknown"
            current_lines = []
        elif line.startswith("+++ ") or line.startswith("--- "):
            continue
        elif line.startswith("@@"):
            current_lines.append({"type": "hunk_header", "text": line})
        elif line.startswith("+") or line.startswith("-"):
            current_lines.append({"type": "change", "text": line})

    if current_file:
        files.append({"file": current_file, "lines": current_lines})
    return files
def classify_line(line_text):
    """Classify a changed line. Returns a noise category or None if intentional."""
    if WHITESPACE_ONLY.match(line_text):
        return "whitespace"
    if COMMENT_ONLY.match(line_text):
        return "comment-only"
    if DOCSTRING_ADD.match(line_text):
        return "docstring-addition"
    if SEMICOLON_CHANGE.match(line_text):
        # Check if ONLY change is semicolon
        stripped = line_text[1:].rstrip(";").rstrip()
        if not stripped.strip():
            return None
        return "semicolon-style"
    return None
def analyze_file_diff(file_data):
    """Analyze a single file's diff for noise."""
    findings = []
    change_lines = [l for l in file_data["lines"] if l["type"] == "change"]
    total_changes = len(change_lines)

    if total_changes == 0:
        return findings

    # Detect paired +/- that are only whitespace/style changes
    additions = [l["text"] for l in change_lines if l["text"].startswith("+")]
    deletions = [l["text"] for l in change_lines if l["text"].startswith("-")]

    noise_count = 0
    for line_data in change_lines:
        category = classify_line(line_data["text"])
        if category:
            noise_count += 1
            findings.append({
                "category": category,
                "line": line_data["text"][:120],
            })

    # Detect quote-style swaps (paired changes where only quotes differ)
    for a, d in zip(sorted(additions), sorted(deletions)):
        a_norm = a[1:].replace('"', "'").strip()
        d_norm = d[1:].replace('"', "'").strip()
        if a_norm == d_norm and a[1:].strip() != d[1:].strip():
            findings.append({
                "category": "quote-style-swap",
                "line": f"{d[:60]} → {a[:60]}",
            })

    noise_ratio = noise_count / total_changes if total_changes > 0 else 0
    return findings

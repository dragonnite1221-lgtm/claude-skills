# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from a11y_scanner_base import *  # noqa: F403,E402
# fmt: off
from a11y_scanner_p1 import Finding, TAG_RE, _attrs, _snippet, check_fieldset_legend, check_orphan_label  # noqa: E402,E501
from a11y_scanner_p2 import check_aria_live_missing, check_headings, check_landmarks, check_text_over_image  # noqa: E402,E501
from a11y_scanner_p3 import SUPPORTED_EXTENSIONS, TAG_LEVEL_CHECKS, TAG_LEVEL_MULTI_CHECKS, check_empty_links_line, check_media_captions_block, check_table_headers  # noqa: E402,E501
# fmt: on


def scan_file(filepath: str) -> List[Finding]:
    """Scan a single file and return all findings."""
    findings: List[Finding] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, IOError):
        return findings

    # Tag-level checks
    for ln, line in enumerate(lines, 1):
        for m in TAG_RE.finditer(line):
            tag = m.group(1).lower()
            attr_str = m.group(2)
            attrs = _attrs(attr_str)
            snip = _snippet(line)
            for check in TAG_LEVEL_CHECKS:
                result = check(tag, attrs, filepath, ln, snip)
                if result:
                    findings.append(result)
            for check in TAG_LEVEL_MULTI_CHECKS:
                results = check(tag, attrs, filepath, ln, snip)
                if results:
                    findings.extend(results)

    # File-level / multi-line checks
    findings.extend(check_orphan_label(lines, filepath))
    findings.extend(check_fieldset_legend(lines, filepath))
    findings.extend(check_headings(lines, filepath))
    findings.extend(check_landmarks(lines, filepath))
    findings.extend(check_aria_live_missing(lines, filepath))
    findings.extend(check_text_over_image(lines, filepath))
    findings.extend(check_empty_links_line(lines, filepath))
    findings.extend(check_table_headers(lines, filepath))
    findings.extend(check_media_captions_block(lines, filepath))

    return findings
def collect_files(path: str) -> List[str]:
    """Recursively collect scannable files under path."""
    files = []
    if os.path.isfile(path):
        _, ext = os.path.splitext(path)
        if ext.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
        return files
    for root, dirs, filenames in os.walk(path):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in (
            "node_modules", ".git", "dist", "build", "__pycache__",
            ".next", ".nuxt", "vendor", "coverage"
        )]
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext.lower() in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(root, fname))
    files.sort()
    return files
SEVERITY_ORDER = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
def format_human(findings: List[Finding], files_scanned: int) -> str:
    """Format findings as human-readable text report."""
    if not findings:
        return (f"Scanned {files_scanned} file(s) -- no accessibility issues found.\n"
                "All checks passed.")

    lines = []
    lines.append(f"WCAG 2.2 Accessibility Scan Results")
    lines.append(f"{'=' * 50}")
    lines.append(f"Files scanned: {files_scanned}")
    lines.append(f"Issues found:  {len(findings)}")

    # Summary by severity
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
    for sev in ("critical", "serious", "moderate", "minor"):
        if sev in severity_counts:
            lines.append(f"  {sev.upper():10s}: {severity_counts[sev]}")
    lines.append("")

    # Summary by category
    cat_counts = {}
    for f in findings:
        cat_counts[f.category] = cat_counts.get(f.category, 0) + 1
    lines.append("By category:")
    for cat in sorted(cat_counts, key=lambda c: -cat_counts[c]):
        lines.append(f"  {cat:20s}: {cat_counts[cat]}")
    lines.append("")

    # Detailed findings sorted by severity then file
    sorted_findings = sorted(findings, key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.file, f.line))
    for i, f in enumerate(sorted_findings, 1):
        lines.append(f"[{f.severity.upper()}] {f.rule_id}")
        lines.append(f"  File: {f.file}:{f.line}")
        lines.append(f"  WCAG: {f.wcag_criterion}")
        lines.append(f"  Issue: {f.message}")
        if f.snippet:
            lines.append(f"  Code:  {f.snippet}")
        lines.append(f"  Fix:   {f.fix}")
        lines.append("")

    return "\n".join(lines)
def format_json(findings: List[Finding], files_scanned: int) -> str:
    """Format findings as JSON."""
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    report = {
        "summary": {
            "files_scanned": files_scanned,
            "total_issues": len(findings),
            "by_severity": severity_counts,
        },
        "findings": [asdict(f) for f in findings],
    }
    return json.dumps(report, indent=2)

# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from secret_scanner_base import *  # noqa: F403,E402
# fmt: off
from secret_scanner_p1 import SecretFinding, SecretPattern, Severity  # noqa: E402,E501
from secret_scanner_p3 import SECRET_PATTERNS, scan_file  # noqa: E402,E501
# fmt: on


def scan_directory(dir_path: Path, patterns: List[SecretPattern],
                   exclude_dirs: List[str] = None) -> List[SecretFinding]:
    """Scan all files in a directory for secrets."""
    if exclude_dirs is None:
        exclude_dirs = [
            "node_modules", ".git", "__pycache__", "venv", ".venv",
            "dist", "build", ".next", "vendor", ".idea", ".vscode"
        ]

    findings = []
    extensions = set()
    for pattern in patterns:
        extensions.update(pattern.file_extensions)

    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            # Check exclusions
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            # Skip binary files and large files
            if file_path.stat().st_size > 1_000_000:  # 1MB limit
                continue

            if file_path.suffix.lower() in extensions or file_path.name in ['.env', '.env.local', '.env.production']:
                findings.extend(scan_file(file_path, patterns))

    return sorted(findings, key=lambda f: (
        0 if f.severity == Severity.CRITICAL else
        1 if f.severity == Severity.HIGH else
        2 if f.severity == Severity.MEDIUM else 3
    ))
def format_text_report(findings: List[SecretFinding], path: str) -> str:
    """Format findings as text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("SECRET SCAN REPORT")
    lines.append("=" * 70)
    lines.append(f"Target: {path}")
    lines.append("")

    # Summary
    by_severity = {}
    for finding in findings:
        sev = finding.severity.value
        by_severity[sev] = by_severity.get(sev, 0) + 1

    lines.append("SUMMARY:")
    lines.append(f"  Total Secrets Found: {len(findings)}")
    for sev in ["critical", "high", "medium", "low"]:
        count = by_severity.get(sev, 0)
        if count > 0:
            lines.append(f"  {sev.upper()}: {count}")
    lines.append("")

    if not findings:
        lines.append("No secrets found!")
        lines.append("=" * 70)
        return "\n".join(lines)

    # Group by severity
    current_severity = None
    for finding in findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            lines.append("-" * 70)
            lines.append(f"[{current_severity.value.upper()}]")
            lines.append("-" * 70)

        lines.append("")
        lines.append(f"  [{finding.pattern_id}] {finding.name}")
        lines.append(f"  File: {finding.file_path}:{finding.line_number}")
        lines.append(f"  Match: {finding.matched_text}")
        lines.append(f"  Fix: {finding.recommendation}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("IMPORTANT: Review all findings and rotate exposed credentials!")
    lines.append("=" * 70)
    return "\n".join(lines)
def format_json_report(findings: List[SecretFinding], path: str) -> Dict:
    """Format findings as JSON."""
    return {
        "target": path,
        "scan_date": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total": len(findings),
            "by_severity": {
                sev.value: sum(1 for f in findings if f.severity == sev)
                for sev in Severity
            }
        },
        "findings": [
            {
                "pattern_id": f.pattern_id,
                "name": f.name,
                "severity": f.severity.value,
                "file_path": f.file_path,
                "line_number": f.line_number,
                "matched_text": f.matched_text,
                "recommendation": f.recommendation
            }
            for f in findings
        ]
    }
def list_patterns():
    """List all secret patterns."""
    print("\n" + "=" * 60)
    print("SECRET DETECTION PATTERNS")
    print("=" * 60)

    for pattern in sorted(SECRET_PATTERNS, key=lambda p: p.pattern_id):
        print(f"\n[{pattern.pattern_id}] {pattern.name}")
        print(f"  Severity: {pattern.severity.value.upper()}")
        print(f"  Description: {pattern.description}")

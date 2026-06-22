# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import AuditReport, Finding, Severity  # noqa: E402,E501
# fmt: on


def scan_filesystem(skill_path: Path, report: AuditReport):
    """Scan the skill directory structure for suspicious files."""
    for item in skill_path.rglob("*"):
        rel = item.relative_to(skill_path)
        rel_str = str(rel)

        # Skip .git directory
        if ".git" in rel.parts:
            continue

        report.files_scanned += 1

        # Hidden files (except common ones)
        if item.name.startswith(".") and item.name not in (
            ".gitignore", ".gitkeep", ".editorconfig", ".prettierrc",
            ".eslintrc", ".pylintrc", ".flake8", ".security-audit-allowlist",
            ".claude-plugin", ".codex", ".gemini",
        ):
            severity = Severity.CRITICAL if item.name == ".env" else Severity.HIGH
            report.findings.append(
                Finding(
                    severity=severity,
                    category="FS-HIDDEN",
                    file=rel_str,
                    line=0,
                    pattern=item.name,
                    risk=f"Hidden file '{item.name}' — may contain secrets or hidden config",
                    fix="Remove hidden files from skill distribution",
                )
            )

        # Binary files
        if item.is_file() and item.suffix.lower() in (
            ".exe", ".dll", ".so", ".dylib", ".bin", ".elf",
            ".com", ".msi", ".deb", ".rpm", ".apk",
        ):
            report.findings.append(
                Finding(
                    severity=Severity.CRITICAL,
                    category="FS-BINARY",
                    file=rel_str,
                    line=0,
                    pattern=item.name,
                    risk="Binary executable in skill — high risk of malicious payload",
                    fix="Remove binary files. Skills should use interpreted scripts only",
                )
            )

        # Large files (>1MB)
        if item.is_file():
            try:
                size = item.stat().st_size
                if size > 1_000_000:
                    report.findings.append(
                        Finding(
                            severity=Severity.INFO,
                            category="FS-LARGE",
                            file=rel_str,
                            line=0,
                            pattern=f"{size / 1_000_000:.1f}MB",
                            risk="Large file — may hide payloads or bloat installation",
                            fix="Review file contents. Consider if this file is necessary",
                        )
                    )
            except OSError:
                pass

        # Symlinks
        if item.is_symlink():
            try:
                target = item.resolve()
                if not str(target).startswith(str(skill_path.resolve())):
                    report.findings.append(
                        Finding(
                            severity=Severity.CRITICAL,
                            category="FS-SYMLINK",
                            file=rel_str,
                            line=0,
                            pattern=f"→ {target}",
                            risk="Symlink points outside skill directory — directory traversal risk",
                            fix="Remove symlinks pointing outside the skill directory",
                        )
                    )
            except (OSError, ValueError):
                pass

        # SUID/SGID bits
        if item.is_file():
            try:
                mode = item.stat().st_mode
                if mode & (stat.S_ISUID | stat.S_ISGID):
                    report.findings.append(
                        Finding(
                            severity=Severity.CRITICAL,
                            category="FS-SUID",
                            file=rel_str,
                            line=0,
                            pattern=f"mode={oct(mode)}",
                            risk="SUID/SGID bit set — privilege escalation risk",
                            fix="Remove SUID/SGID bits: chmod u-s,g-s <file>",
                        )
                    )
            except OSError:
                pass
def load_allowlist(skill_path: Path) -> list:
    """Load per-skill audit suppressions from `.security-audit-allowlist`.

    Each non-comment line is a rule `CATEGORY <relpath>[:line]`. A finding is
    suppressed when its category and file (and line, if given) match. This is
    the auditable escape hatch for security-tooling skills that legitimately
    contain the patterns they detect (e.g. attack examples documented in a
    threat model). Detection strength is unchanged for every other skill —
    exceptions are explicit, per-skill, and reviewable in one file."""
    allowlist_file = skill_path / ".security-audit-allowlist"
    rules = []
    if not allowlist_file.exists():
        return rules
    for raw in allowlist_file.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        category = parts[0]
        target = parts[1]
        relpath, _, lineno = target.partition(":")
        rules.append((category, relpath, lineno or None))
    return rules

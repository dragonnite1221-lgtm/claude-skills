# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import AuditReport, Finding, Severity  # noqa: E402,E501
from skill_security_auditor_p5 import CODE_EXTENSIONS, TYPOSQUAT_TARGETS, is_test_artifact  # noqa: E402,E501
from skill_security_auditor_p6 import mask_python_noncode  # noqa: E402,E501
# fmt: on


def scan_dependencies(skill_path: Path, report: AuditReport):
    """Scan dependency files for supply chain risks."""
    # Check requirements.txt
    req_file = skill_path / "requirements.txt"
    if req_file.exists():
        try:
            lines = req_file.read_text().split("\n")
        except Exception:
            return

        all_typosquats = {}
        for real_pkg, fakes in TYPOSQUAT_TARGETS.items():
            for fake in fakes:
                all_typosquats[fake.lower()] = real_pkg

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Extract package name
            pkg_name = re.split(r"[>=<!\[;]", line)[0].strip().lower()

            # Typosquatting check
            if pkg_name in all_typosquats:
                report.findings.append(
                    Finding(
                        severity=Severity.HIGH,
                        category="DEPS-TYPOSQUAT",
                        file=str(req_file),
                        line=i,
                        pattern=line,
                        risk=f"Possible typosquatting — did you mean '{all_typosquats[pkg_name]}'?",
                        fix=f"Verify package name. Likely should be '{all_typosquats[pkg_name]}'",
                    )
                )

            # Unpinned version check
            if pkg_name and "==" not in line and pkg_name not in (".", "-e", "-r"):
                report.findings.append(
                    Finding(
                        severity=Severity.INFO,
                        category="DEPS-UNPIN",
                        file=str(req_file),
                        line=i,
                        pattern=line,
                        risk="Unpinned dependency — may pull vulnerable versions",
                        fix=f"Pin to specific version: {pkg_name}==<version>",
                    )
                )

    # Check for pip/npm install in code
    for code_file in skill_path.rglob("*"):
        if code_file.suffix.lower() not in CODE_EXTENSIONS or is_test_artifact(code_file):
            continue
        try:
            content = code_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        ext = code_file.suffix.lower()
        # Match only executable code: blank string/comment text for Python and
        # skip comment lines, so a literal "pip install" in a docstring or
        # comment is not flagged as a runtime install.
        scan_src = mask_python_noncode(content) if ext == ".py" else content
        for i, line in enumerate(scan_src.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#") and ext in {".py", ".sh", ".bash"}:
                continue
            if re.search(r"\bpip\s+install\b", line):
                report.findings.append(
                    Finding(
                        severity=Severity.HIGH,
                        category="DEPS-RUNTIME",
                        file=str(code_file),
                        line=i,
                        pattern=line.strip()[:120],
                        risk="Runtime package installation — may install untrusted code",
                        fix="Move dependencies to requirements.txt for pre-install review",
                    )
                )
            if re.search(r"\bnpm\s+install\b|\byarn\s+add\b|\bpnpm\s+add\b", line):
                report.findings.append(
                    Finding(
                        severity=Severity.HIGH,
                        category="DEPS-RUNTIME",
                        file=str(code_file),
                        line=i,
                        pattern=line.strip()[:120],
                        risk="Runtime package installation — may install untrusted code",
                        fix="Move dependencies to package.json for pre-install review",
                    )
                )

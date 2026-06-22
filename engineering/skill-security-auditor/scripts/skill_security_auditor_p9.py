# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import AuditReport, Finding, Severity  # noqa: E402,E501
from skill_security_auditor_p5 import CODE_EXTENSIONS, MD_EXTENSIONS, is_test_artifact  # noqa: E402,E501
from skill_security_auditor_p6 import scan_file_code, scan_file_prompt_injection  # noqa: E402,E501
from skill_security_auditor_p7 import scan_dependencies  # noqa: E402,E501
from skill_security_auditor_p8 import load_allowlist, scan_filesystem  # noqa: E402,E501
# fmt: on


def _is_allowlisted(finding: "Finding", rules: list, skill_path: Path) -> bool:
    try:
        rel = Path(finding.file).resolve().relative_to(skill_path.resolve()).as_posix()
    except ValueError:
        rel = Path(finding.file).name
    for category, relpath, lineno in rules:
        if finding.category != category:
            continue
        if rel != relpath:
            continue
        if lineno is not None and str(finding.line) != lineno:
            continue
        return True
    return False
def scan_skill(skill_path: Path) -> AuditReport:
    """Run full security audit on a skill directory."""
    report = AuditReport(
        skill_name=skill_path.name,
        skill_path=str(skill_path),
    )

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        report.findings.append(
            Finding(
                severity=Severity.HIGH,
                category="STRUCTURE",
                file="SKILL.md",
                line=0,
                pattern="SKILL.md not found",
                risk="Missing SKILL.md — not a valid skill directory",
                fix="Ensure the path points to a valid skill directory with SKILL.md",
            )
        )

    # 1. Filesystem scan
    scan_filesystem(skill_path, report)

    # 2. Code scanning (test fixtures are excluded — see is_test_artifact)
    for code_file in skill_path.rglob("*"):
        if ".git" in code_file.parts or is_test_artifact(code_file):
            continue
        if code_file.is_file() and code_file.suffix.lower() in CODE_EXTENSIONS:
            report.scripts_scanned += 1
            scan_file_code(code_file, report)

    # 3. Prompt injection scanning
    for md_file in skill_path.rglob("*"):
        if ".git" in md_file.parts:
            continue
        if md_file.is_file() and md_file.suffix.lower() in MD_EXTENSIONS:
            report.md_files_scanned += 1
            scan_file_prompt_injection(md_file, report)

    # 4. Dependency scanning
    scan_dependencies(skill_path, report)

    # 5. Apply per-skill allowlist (auditable suppressions)
    rules = load_allowlist(skill_path)
    if rules:
        report.findings = [
            f for f in report.findings if not _is_allowlisted(f, rules, skill_path)
        ]

    return report
def clone_repo(url: str, skill_name: Optional[str] = None, cleanup: bool = False):
    """Clone a git repo to a temp directory and return the skill path."""
    tmp_dir = tempfile.mkdtemp(prefix="skill-audit-")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, tmp_dir],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error cloning {url}: {e.stderr}", file=sys.stderr)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    if skill_name:
        skill_path = Path(tmp_dir) / skill_name
        if not skill_path.exists():
            # Try finding it
            matches = list(Path(tmp_dir).rglob(skill_name))
            if matches:
                skill_path = matches[0]
            else:
                print(f"Skill '{skill_name}' not found in repo", file=sys.stderr)
                shutil.rmtree(tmp_dir, ignore_errors=True)
                sys.exit(1)
    else:
        skill_path = Path(tmp_dir)

    return skill_path, tmp_dir if cleanup else None

"""Regression tests for the security auditor's false-positive fixes.

A security/validation tool legitimately CONTAINS the patterns it detects (in
docstrings, pattern-definition strings, and test fixtures). The auditor must
not flag those, while still catching real dangerous calls in normal skills.
These tests pin that behavior so it cannot silently regress."""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDITOR = REPO_ROOT / "engineering" / "skill-security-auditor" / "scripts" / "skill_security_auditor.py"

spec = importlib.util.spec_from_file_location("skill_security_auditor", AUDITOR)
auditor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = auditor
spec.loader.exec_module(auditor)


def _make_skill(tmp_path, files: dict):
    (tmp_path / "SKILL.md").write_text("---\nname: t\ndescription: d\n---\n# T\n")
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return tmp_path


def _categories(report):
    return [f.category for f in report.findings]


def test_real_dangerous_call_is_detected(tmp_path):
    _make_skill(tmp_path, {"run.py": "import os\nos.system(user_input)\n"})
    report = auditor.scan_skill(tmp_path)
    assert "CMD-INJECT" in _categories(report)


def test_docstring_pattern_is_not_flagged(tmp_path):
    # The string content names os.system()/eval() but executes nothing.
    _make_skill(tmp_path, {"scorer.py": '"""Detects:\n- os.system() usage\n- eval(), exec() usage\n"""\nx = 1\n'})
    report = auditor.scan_skill(tmp_path)
    assert _categories(report) == [], _categories(report)


def test_test_fixtures_are_skipped(tmp_path):
    _make_skill(tmp_path, {"tests/test_x.py": "code = 'os.system(\"ls\")'\neval('1')\n"})
    report = auditor.scan_skill(tmp_path)
    assert _categories(report) == [], _categories(report)


def test_allowlist_suppresses_named_findings(tmp_path):
    _make_skill(tmp_path, {"run.py": "import os\nos.system(x)\n"})
    report = auditor.scan_skill(tmp_path)
    assert "CMD-INJECT" in _categories(report)
    (tmp_path / ".security-audit-allowlist").write_text("CMD-INJECT run.py  # intentional\n")
    report2 = auditor.scan_skill(tmp_path)
    assert "CMD-INJECT" not in _categories(report2)

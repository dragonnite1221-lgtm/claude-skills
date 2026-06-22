"""Regression tests pinning skill_validator.py to the repo's real skill contract.

The structural validator (engineering/skill-tester) previously required a
frontmatter/section schema (Tier/Category/Author/Version, Features/Usage/
Examples) that NO skill in this repo uses — 237/238 skills failed the same two
checks, including Tessl-100/100 skills. That made its score meaningless.

These tests lock the validator to the *enforced* contract
(`scripts/validate-skill-frontmatter.py` + Tessl): frontmatter is
`name` + `description`, body sections are not mandated, and scripts/ is
optional. If someone reverts to the old schema, these fail."""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "engineering" / "skill-tester" / "scripts" / "skill_validator.py"

spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR)
skill_validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = skill_validator
spec.loader.exec_module(skill_validator)


def _validate(skill_dir: str):
    v = skill_validator.SkillValidator(str(REPO_ROOT / skill_dir))
    report = v.validate_skill_structure()
    report.calculate_overall_score()
    return report


def test_frontmatter_required_fields_match_enforced_contract():
    assert skill_validator.SkillValidator.FRONTMATTER_REQUIRED_FIELDS == ["name", "description"]


def test_no_mandated_body_sections():
    # An empty section list means "title only"; the repo does not mandate
    # Features/Usage/Examples headings (Tessl rewards removing them).
    assert skill_validator.SkillValidator.REQUIRED_SKILL_MD_SECTIONS == []


def test_real_skill_validates_cleanly():
    """A representative real skill (name+description frontmatter, no README,
    no scripts/, ~75 lines) must validate with NO errors — i.e. the CLI would
    exit 0 — not merely score >= 70 while still raising contract errors."""
    report = _validate("c-level-advisor/cs-onboard")
    assert report.checks["frontmatter_complete"]["passed"], report.checks["frontmatter_complete"]
    assert report.checks["skill_md_title"]["passed"], report.checks["skill_md_title"]
    # README is advisory, never a penalty.
    assert report.checks["readme_present"]["passed"]
    # No tier targeted => scripts/ is not a required directory.
    assert "dir_scripts_exists" not in report.checks
    # Honest "passes": the CLI exits non-zero when report.errors is non-empty,
    # so a clean skill must produce zero errors, not just a high score.
    assert report.errors == [], report.errors
    assert report.overall_score >= 70.0, report.overall_score


def test_tessl_100_skill_is_not_penalized_on_contract():
    """senior-data-engineer scores 100/100 on Tessl; the structural validator
    must not false-fail it on the *contract* (frontmatter, title, length,
    single-quote main guard). Any remaining errors must be real findings
    (e.g. an external import), never the unused-schema or quote-style bugs."""
    report = _validate("engineering-team/senior-data-engineer")
    assert report.checks["frontmatter_complete"]["passed"]
    assert report.checks["skill_md_title"]["passed"]
    assert report.checks["skill_md_length"]["passed"], "78-line skill must not be 'too short'"
    # Single-quote `if __name__ == '__main__'` guards must be detected.
    guard_checks = {k: v for k, v in report.checks.items() if k.startswith("script_main_guard_")}
    assert guard_checks and all(c["passed"] for c in guard_checks.values()), guard_checks
    # No contract/quote-bug errors should remain; only substantive findings.
    for err in report.errors:
        assert "too short" not in err and "main guard" not in err, err
    assert report.overall_score >= 70.0, report.overall_score

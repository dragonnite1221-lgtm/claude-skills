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


def _score(skill_dir: str) -> tuple[float, dict]:
    v = skill_validator.SkillValidator(str(REPO_ROOT / skill_dir))
    report = v.validate_skill_structure()
    report.calculate_overall_score()
    return report.overall_score, report.checks


def test_frontmatter_required_fields_match_enforced_contract():
    assert skill_validator.SkillValidator.FRONTMATTER_REQUIRED_FIELDS == ["name", "description"]


def test_no_mandated_body_sections():
    # An empty section list means "title only"; the repo does not mandate
    # Features/Usage/Examples headings (Tessl rewards removing them).
    assert skill_validator.SkillValidator.REQUIRED_SKILL_MD_SECTIONS == []


def test_real_skill_passes_contract_checks():
    """A representative real skill (name+description frontmatter, no README,
    no scripts/) must pass the contract checks rather than false-fail."""
    score, checks = _score("c-level-advisor/cs-onboard")
    assert checks["frontmatter_complete"]["passed"], checks["frontmatter_complete"]
    assert checks["skill_md_title"]["passed"], checks["skill_md_title"]
    # README is advisory, never a penalty.
    assert checks["readme_present"]["passed"]
    # No tier targeted => scripts/ is not a required directory.
    assert "dir_scripts_exists" not in checks
    assert score >= 70.0, f"contract-compliant skill scored {score}"


def test_tessl_100_skill_is_not_penalized():
    """senior-data-engineer scores 100/100 on Tessl; it must not be dragged
    down by the structural validator demanding an unused schema."""
    score, checks = _score("engineering-team/senior-data-engineer")
    assert checks["frontmatter_complete"]["passed"]
    assert score >= 70.0, f"Tessl-100 skill scored {score}"

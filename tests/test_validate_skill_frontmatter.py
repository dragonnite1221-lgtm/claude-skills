"""Tests for the SKILL.md frontmatter and Gemini mirror gate."""

import importlib.util
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate-skill-frontmatter.py"

spec = importlib.util.spec_from_file_location("validate_skill_frontmatter", SCRIPT_PATH)
validate_skill_frontmatter = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = validate_skill_frontmatter
spec.loader.exec_module(validate_skill_frontmatter)


def test_parse_frontmatter_does_not_accept_prefixed_description(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: demo\n"
        "description_url: https://example.com\n"
        "---\n"
        "# Demo\n",
        encoding="utf-8",
    )

    fields = validate_skill_frontmatter.parse_frontmatter_fields(skill_md)

    assert fields["name"] == "demo"
    assert "description_url" in fields
    assert "description" not in fields


def test_parse_frontmatter_block_scalar_description(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: demo\n"
        "description: >-\n"
        "  Use this skill for demos.\n"
        "  Keep the second line too.\n"
        "---\n"
        "# Demo\n",
        encoding="utf-8",
    )

    fields = validate_skill_frontmatter.parse_frontmatter_fields(skill_md)

    assert fields["description"] == "Use this skill for demos.\nKeep the second line too."


def test_validate_skill_frontmatter_reports_external_source(tmp_path):
    skills = [
        {
            "name": "external",
            "source": "/tmp/outside/SKILL.md",
            "category": "engineering",
            "description": "external",
        }
    ]

    issues = validate_skill_frontmatter.validate_skill_frontmatter(tmp_path, skills, set())

    assert [issue.code for issue in issues] == ["external_source"]


def test_validate_current_repository_frontmatter_and_mirror():
    issues = validate_skill_frontmatter.validate_repo(REPO_ROOT)

    assert issues == []


def test_allowlist_is_narrow_and_repo_relative():
    allowlist = validate_skill_frontmatter.DEFAULT_FRONTMATTER_ALLOWLIST

    assert allowlist == {"engineering/skill-tester/assets/sample-skill/SKILL.md"}
    assert all(not os.path.isabs(path) for path in allowlist)

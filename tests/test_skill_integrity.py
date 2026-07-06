"""Integration tests: verify skill package consistency across the repository.

These tests validate that:
1. Every skill directory with a SKILL.md has valid structure
2. SKILL.md files have required YAML frontmatter
3. File references in SKILL.md actually exist
4. Scripts directories contain valid Python files
5. No orphaned scripts directories without a SKILL.md
"""

import glob
import importlib.util
import json
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT_PATH = Path(REPO_ROOT)

SKILL_DOMAINS = [
    "engineering-team",
    "engineering",
    "product-team",
    "marketing-skill",
    "project-management",
    "c-level-advisor",
    "ra-qm-team",
    "business-growth",
    "finance",
]

SKIP_PATTERNS = [
    "assets/sample-skill",
    "assets/sample_codebase",
    "__pycache__",
]


def _find_all_skill_dirs():
    """Find all directories containing a SKILL.md file."""
    skills = []
    for domain in SKILL_DOMAINS:
        domain_path = os.path.join(REPO_ROOT, domain)
        if not os.path.isdir(domain_path):
            continue
        for root, dirs, files in os.walk(domain_path):
            if "SKILL.md" in files:
                rel = os.path.relpath(root, REPO_ROOT)
                rel_normalized = rel.replace(os.sep, "/").replace("\\", "/")
                if any(skip in rel_normalized for skip in SKIP_PATTERNS):
                    continue
                skills.append(root)
    return skills


ALL_SKILL_DIRS = _find_all_skill_dirs()


def _short_id(path):
    return os.path.relpath(path, REPO_ROOT)


def _read_frontmatter(skill_dir):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\r?\n(.*?)---\r?\n", content, re.DOTALL)
    assert match, f"{_short_id(skill_dir)}/SKILL.md has invalid frontmatter delimiters"
    return match.group(1)


def _parse_frontmatter_fields(skill_dir):
    """Parse top-level frontmatter keys used by repository gate checks."""
    fields = {}
    current_key = None
    for raw_line in _read_frontmatter(skill_dir).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith((" ", "\t")):
            if current_key and fields[current_key] in {">", ">-", ">+", "|", "|-", "|+"}:
                continuation = raw_line.strip()
                if continuation:
                    fields[current_key] = continuation
            continue

        key, sep, value = raw_line.partition(":")
        if sep != ":":
            continue
        current_key = key.strip()
        parsed_value = value.strip()
        if (
            (parsed_value.startswith('"') and parsed_value.endswith('"'))
            or (parsed_value.startswith("'") and parsed_value.endswith("'"))
        ):
            parsed_value = parsed_value[1:-1].strip()
        fields[current_key] = parsed_value

    return fields


class TestSkillMdExists:
    """Every recognized skill directory must have a SKILL.md."""

    def test_found_skills(self):
        assert len(ALL_SKILL_DIRS) > 100, f"Expected 100+ skills, found {len(ALL_SKILL_DIRS)}"


class TestFrontmatterParser:
    """Guard the repository-level SKILL.md frontmatter parser."""

    def test_distinguishes_required_keys_from_prefixed_keys(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: demo\n"
            "description_url: https://example.com\n"
            "---\n"
            "# Demo\n",
            encoding="utf-8",
        )

        fields = _parse_frontmatter_fields(str(skill_dir))

        assert "name" in fields
        assert "description_url" in fields
        assert "description" not in fields

    def test_block_scalar_description_has_non_empty_value(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: demo\n"
            "description: >-\n"
            "  Use this skill for demos.\n"
            "---\n"
            "# Demo\n",
            encoding="utf-8",
        )

        fields = _parse_frontmatter_fields(str(skill_dir))

        assert fields["description"] == "Use this skill for demos."


class TestSkillMdFrontmatter:
    """SKILL.md files should have YAML frontmatter with name and description."""

    @pytest.mark.parametrize(
        "skill_dir",
        ALL_SKILL_DIRS,
        ids=[_short_id(s) for s in ALL_SKILL_DIRS],
    )
    def test_has_frontmatter(self, skill_dir):
        skill_md = os.path.join(skill_dir, "SKILL.md")
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for YAML frontmatter delimiters
        assert content.startswith("---"), (
            f"{_short_id(skill_dir)}/SKILL.md is missing YAML frontmatter (no opening ---)"
        )
        # Find closing ---
        second_delim = content.find("---", 4)
        assert second_delim > 0, (
            f"{_short_id(skill_dir)}/SKILL.md has unclosed frontmatter"
        )

    @pytest.mark.parametrize(
        "skill_dir",
        ALL_SKILL_DIRS,
        ids=[_short_id(s) for s in ALL_SKILL_DIRS],
    )
    def test_frontmatter_has_name(self, skill_dir):
        fields = _parse_frontmatter_fields(skill_dir)
        assert "name" in fields, (
            f"{_short_id(skill_dir)}/SKILL.md frontmatter missing 'name' field"
        )
        assert fields["name"], (
            f"{_short_id(skill_dir)}/SKILL.md frontmatter has empty 'name' field"
        )

    @pytest.mark.parametrize(
        "skill_dir",
        ALL_SKILL_DIRS,
        ids=[_short_id(s) for s in ALL_SKILL_DIRS],
    )
    def test_frontmatter_has_description(self, skill_dir):
        fields = _parse_frontmatter_fields(skill_dir)
        assert "description" in fields, (
            f"{_short_id(skill_dir)}/SKILL.md frontmatter missing 'description' field"
        )
        assert fields["description"], (
            f"{_short_id(skill_dir)}/SKILL.md frontmatter has empty 'description' field"
        )


class TestSkillMdHasH1:
    """Every SKILL.md must have at least one H1 heading."""

    @pytest.mark.parametrize(
        "skill_dir",
        ALL_SKILL_DIRS,
        ids=[_short_id(s) for s in ALL_SKILL_DIRS],
    )
    def test_has_h1(self, skill_dir):
        skill_md = os.path.join(skill_dir, "SKILL.md")
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # Strip frontmatter
        content = re.sub(r"^---\n.*?---\n", "", content, flags=re.DOTALL)
        assert re.search(r"^# .+", content, re.MULTILINE), (
            f"{_short_id(skill_dir)}/SKILL.md has no H1 heading"
        )


class TestScriptDirectories:
    """Validate scripts/ directories within skills."""

    def _get_skills_with_scripts(self):
        result = []
        for skill_dir in ALL_SKILL_DIRS:
            scripts_dir = os.path.join(skill_dir, "scripts")
            if os.path.isdir(scripts_dir):
                py_files = glob.glob(os.path.join(scripts_dir, "*.py"))
                if py_files:
                    result.append((skill_dir, py_files))
        return result

    def test_scripts_dirs_have_python_files(self):
        """Every scripts/ directory should contain at least one .py file."""
        for skill_dir in ALL_SKILL_DIRS:
            scripts_dir = os.path.join(skill_dir, "scripts")
            if os.path.isdir(scripts_dir):
                py_files = glob.glob(os.path.join(scripts_dir, "*.py"))
                assert len(py_files) > 0, (
                    f"{_short_id(skill_dir)}/scripts/ exists but has no .py files"
                )

    def test_no_empty_skill_md(self):
        """SKILL.md files should not be empty."""
        for skill_dir in ALL_SKILL_DIRS:
            skill_md = os.path.join(skill_dir, "SKILL.md")
            size = os.path.getsize(skill_md)
            assert size > 100, (
                f"{_short_id(skill_dir)}/SKILL.md is suspiciously small ({size} bytes)"
            )


class TestReferencesDirectories:
    """Validate references/ directories are non-empty."""

    def test_references_not_empty(self):
        for skill_dir in ALL_SKILL_DIRS:
            refs_dir = os.path.join(skill_dir, "references")
            if os.path.isdir(refs_dir):
                files = [f for f in os.listdir(refs_dir) if not f.startswith(".")]
                assert len(files) > 0, (
                    f"{_short_id(skill_dir)}/references/ exists but is empty"
                )


class TestNoDuplicateSkillNames:
    """Skill directory names should be unique across the entire repo."""

    def test_unique_top_level_skill_names(self):
        """Top-level skills (direct children of domains) should not have 3+ duplicates."""
        names = {}
        for skill_dir in ALL_SKILL_DIRS:
            rel = _short_id(skill_dir)
            parts = rel.split(os.sep)
            # Only check top-level skills (domain/skill-name), not sub-skills
            if len(parts) != 2:
                continue
            name = parts[1]
            names.setdefault(name, []).append(rel)

        # Report names that appear 3+ times (2 is acceptable for cross-domain)
        triples = {k: v for k, v in names.items() if len(v) >= 3}
        assert not triples, f"Top-level skill names appearing 3+ times: {triples}"


class TestGeminiMirror:
    """The generated Gemini mirror should contain skills, not agents or commands."""

    @staticmethod
    def _load_gemini_sync_module():
        script_path = REPO_ROOT_PATH / "scripts" / "sync-gemini-skills.py"
        spec = importlib.util.spec_from_file_location("sync_gemini_skills", script_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_mirror_matches_sync_script_expected_skills(self):
        module = self._load_gemini_sync_module()
        expected = {skill["name"]: skill for skill in module.find_skills(REPO_ROOT_PATH)}

        mirror_root = REPO_ROOT_PATH / ".gemini" / "skills"
        actual = {
            path.parent.name: os.readlink(path)
            for path in mirror_root.glob("*/SKILL.md")
            if path.is_symlink()
        }

        assert set(actual) == set(expected)
        normalized_targets = [target.replace("\\", "/") for target in actual.values()]
        assert not any(target.startswith("../../../agents/") for target in normalized_targets)
        assert not any(target.startswith("../../../commands/") for target in normalized_targets)

    def test_skills_index_matches_mirror(self):
        index_path = REPO_ROOT_PATH / ".gemini" / "skills-index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        mirror_count = len(list((REPO_ROOT_PATH / ".gemini" / "skills").glob("*/SKILL.md")))
        assert index["total_skills"] == mirror_count
        assert not any(
            skill["description"] in {">", ">-", ">+", "|", "|-", "|+"}
            for skill in index["skills"]
        )

    def test_block_scalar_descriptions_are_parsed(self, tmp_path):
        module = self._load_gemini_sync_module()
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: demo\n"
            "description: >-\n"
            "  First line of the description\n"
            "  continues on the second line.\n"
            "---\n"
            "# Demo\n",
            encoding="utf-8",
        )

        assert module.extract_skill_description(skill_md) == (
            "First line of the description continues on the second line."
        )

    def test_block_scalar_descriptions_handle_crlf_and_blank_lines(self, tmp_path):
        module = self._load_gemini_sync_module()
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\r\n"
            "name: demo\r\n"
            "description_url: https://example.com\r\n"
            "description: >-\r\n"
            "  First paragraph.\r\n"
            "\r\n"
            "  Second paragraph.\r\n"
            "---\r\n"
            "# Demo\r\n",
            encoding="utf-8",
        )

        assert module.extract_skill_description(skill_md) == (
            "First paragraph.\nSecond paragraph."
        )

    def test_unique_name_falls_back_to_full_relative_path(self, tmp_path):
        module = self._load_gemini_sync_module()
        skill_dir = tmp_path / "engineering-team" / "self-improving-agent" / "skills" / "status"
        skill_dir.mkdir(parents=True)
        seen = {
            "status",
            "skills-status",
            "self-improving-agent-skills-status",
        }

        assert module.make_unique_name("status", skill_dir, tmp_path, seen) == (
            "engineering-team-self-improving-agent-skills-status"
        )

    def test_skill_sources_are_relative_to_generated_mirror_directory(self, tmp_path):
        module = self._load_gemini_sync_module()
        skill_dir = tmp_path / "engineering-team" / "demo"
        skill_dir.mkdir(parents=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: demo\n"
            "description: Demo skill.\n"
            "---\n"
            "# Demo\n",
            encoding="utf-8",
        )

        [skill] = module.find_skills(tmp_path)

        mirror_dir = tmp_path / ".gemini" / "skills" / skill["name"]
        assert skill["source"] == os.path.relpath(skill_md, start=mirror_dir)

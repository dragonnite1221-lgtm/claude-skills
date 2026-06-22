# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_skill_integrity_base import *  # noqa: F403,E402
# fmt: off
from test_skill_integrity_p1 import REPO_ROOT_PATH  # noqa: E402,E501
# fmt: on


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

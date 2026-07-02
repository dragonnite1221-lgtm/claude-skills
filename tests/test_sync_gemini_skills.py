"""Tests for Gemini skill mirror generation."""

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "sync-gemini-skills.py"

spec = importlib.util.spec_from_file_location("sync_gemini_skills", SCRIPT_PATH)
sync_gemini_skills = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = sync_gemini_skills
spec.loader.exec_module(sync_gemini_skills)


def write_skill(path: Path, name: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {name} description\n"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )


def test_duplicate_skill_names_are_assigned_deterministically(tmp_path):
    repo_root = tmp_path

    # Create the later path first. Mirror names should still follow sorted
    # repo-relative path order, not filesystem creation order.
    write_skill(repo_root / "engineering" / "b" / "skills" / "status", "status")
    write_skill(repo_root / "engineering" / "a" / "skills" / "status", "status")

    skills = sync_gemini_skills.find_skills(repo_root)
    by_name = {skill["name"]: skill for skill in skills}

    assert by_name["status"]["source"] == "../../../engineering/a/skills/status/SKILL.md"
    assert by_name["skills-status"]["source"] == "../../../engineering/b/skills/status/SKILL.md"

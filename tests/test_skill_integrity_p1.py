# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_skill_integrity_base import *  # noqa: F403,E402


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

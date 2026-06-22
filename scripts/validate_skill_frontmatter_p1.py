# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from validate_skill_frontmatter_base import *  # noqa: F403,E402


FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
DEFAULT_FRONTMATTER_ALLOWLIST = {
    "engineering/skill-tester/assets/sample-skill/SKILL.md",
}
@dataclass
class ValidationIssue:
    code: str
    path: str
    message: str
def load_gemini_sync_module(repo_root: Path):
    script_path = repo_root / "scripts" / "sync-gemini-skills.py"
    spec = importlib.util.spec_from_file_location("sync_gemini_skills", script_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def normalize_repo_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)
def is_under_repo(path: Path, repo_root: Path) -> bool:
    try:
        path.relative_to(repo_root)
    except ValueError:
        return False
    return True
def source_path_for_skill(repo_root: Path, skill: dict[str, Any]) -> Path:
    mirror_dir = repo_root / ".gemini" / "skills" / skill["name"]
    return (mirror_dir / skill["source"]).resolve(strict=False)
def parse_frontmatter_fields(skill_md: Path) -> dict[str, str]:
    content = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    fields: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            index += 1
            continue

        if raw_line.startswith((" ", "\t")):
            index += 1
            continue

        key, separator, value = raw_line.partition(":")
        if separator != ":":
            index += 1
            continue

        field_name = key.strip()
        parsed_value = value.strip()
        if parsed_value in {">", ">-", ">+", "|", "|-", "|+"}:
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if (
                    next_line
                    and not next_line.startswith((" ", "\t"))
                    and ":" in next_line
                ):
                    break
                stripped = next_line.strip()
                if stripped and not stripped.startswith("#"):
                    block_lines.append(stripped)
                index += 1
            fields[field_name] = "\n".join(block_lines).strip()
            continue

        if (
            (parsed_value.startswith('"') and parsed_value.endswith('"'))
            or (parsed_value.startswith("'") and parsed_value.endswith("'"))
        ):
            parsed_value = parsed_value[1:-1].strip()
        fields[field_name] = parsed_value
        index += 1

    return fields

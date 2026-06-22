# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_gemini_skills_base import *  # noqa: F403,E402


try:
    import yaml
except ImportError:
    yaml = None
DOMAIN_MAP = {
    "marketing-skill": "marketing",
    "engineering-team": "engineering",
    "engineering": "engineering-advanced",
    "product-team": "product",
    "c-level-advisor": "c-level",
    "project-management": "project-management",
    "ra-qm-team": "ra-qm",
    "business-growth": "business-growth",
    "finance": "finance"
}
def make_unique_name(skill_name: str, skill_dir: Path, repo_root: Path, seen_names: set) -> str:
    """
    Return a stable unique mirror name.

    Some compound skills contain sub-skills with common names such as
    `status`. Prefixing only the immediate parent (`skills-status`) can still
    collide across different compound skills, so keep walking upward until the
    generated name is unique.
    """
    if skill_name not in seen_names:
        return skill_name

    rel_parts = skill_dir.relative_to(repo_root).parts
    prefix_parts: List[str] = []
    for part in reversed(rel_parts[:-1]):
        prefix_parts.insert(0, part)
        candidate = "-".join(prefix_parts + [skill_name])
        if candidate not in seen_names:
            return candidate

    path_candidate = "-".join(rel_parts)
    if path_candidate not in seen_names:
        return path_candidate

    counter = 2
    while f"{path_candidate}-{counter}" in seen_names:
        counter += 1
    return f"{path_candidate}-{counter}"
def iter_skill_files(repo_root: Path) -> List[Path]:
    """Return SKILL.md files in deterministic repository-relative order."""
    return sorted(
        repo_root.rglob("SKILL.md"),
        key=lambda path: path.relative_to(repo_root).as_posix(),
    )
def extract_skill_description(skill_md_path: Path) -> Optional[str]:
    """
    Extract description from YAML frontmatter.
    """
    try:
        content = skill_md_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return None
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return None
        frontmatter = content[3:end_idx]
        if yaml is not None:
            parsed = yaml.safe_load(frontmatter)
            if isinstance(parsed, dict):
                desc = parsed.get("description")
                if isinstance(desc, str):
                    return desc.strip()
        return None
    except Exception:
        return None
def find_skills(repo_root: Path) -> List[Dict]:
    """
    Scan repository for all skills (SKILL.md files).
    """
    skills = []
    seen_names = set()

    # 1. Find all SKILL.md files recursively. Keep the scan order stable so
    # duplicate skill names get the same generated mirror names on every host.
    for skill_md in iter_skill_files(repo_root):
        # Skip internal .gemini directory
        if ".gemini" in skill_md.parts:
            continue
        
        # Skip evaluation workspaces, assets, and gitignored directories
        if "eval-workspace" in skill_md.parts or "assets" in skill_md.parts or "evals" in skill_md.parts:
            if "sample-skill" not in skill_md.parts: # Keep sample if it's for testing
                continue

        # Skip directories not in DOMAIN_MAP (e.g. agents, commands, docs, local folders)
        top_level = skill_md.relative_to(repo_root).parts[0]
        if top_level not in DOMAIN_MAP:
            continue

        skill_dir = skill_md.parent
        
        # Determine skill name
        if skill_dir == repo_root:
            continue # Root SKILL.md (unlikely)
            
        # For domain-level SKILL.md, name it after the domain
        if skill_dir.name in DOMAIN_MAP:
            skill_name = f"{skill_dir.name}-bundle"
        else:
            skill_name = skill_dir.name

        skill_name = make_unique_name(skill_name, skill_dir, repo_root, seen_names)
        
        seen_names.add(skill_name)
        
        # Determine category from the repository-relative top-level folder.
        category = DOMAIN_MAP.get(top_level, "general")

        description = extract_skill_description(skill_md)
        
        # Calculate the target relative to the concrete mirror directory.
        rel_path = skill_md.relative_to(repo_root)
        mirror_dir = repo_root / ".gemini" / "skills" / skill_name
        source_path = os.path.relpath(skill_md, start=mirror_dir)

        skills.append({
            "name": skill_name,
            "source": source_path,
            "category": category,
            "description": description or f"Skill from {rel_path.parent}"
        })

    skills.sort(key=lambda s: (s["category"], s["name"]))
    return skills

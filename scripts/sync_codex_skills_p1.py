# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_codex_skills_base import *  # noqa: F403,E402


SKILL_DOMAINS = {
    "marketing-skill": {
        "category": "marketing",
        "description": "Marketing, content, and demand generation skills"
    },
    "engineering-team": {
        "category": "engineering",
        "description": "Software engineering and technical skills"
    },
    "engineering": {
        "category": "engineering-advanced",
        "description": "Advanced engineering skills - agents, RAG, MCP, CI/CD, databases, observability"
    },
    "product-team": {
        "category": "product",
        "description": "Product management and design skills"
    },
    "c-level-advisor": {
        "category": "c-level",
        "description": "Executive leadership and advisory skills"
    },
    "project-management": {
        "category": "project-management",
        "description": "Project management and Atlassian skills"
    },
    "ra-qm-team": {
        "category": "ra-qm",
        "description": "Regulatory affairs and quality management skills"
    },
    "business-growth": {
        "category": "business-growth",
        "description": "Customer success, sales engineering, and revenue operations skills"
    },
    "finance": {
        "category": "finance",
        "description": "Financial analysis, valuation, and forecasting skills"
    }
}
def extract_skill_description(skill_md_path: Path) -> Optional[str]:
    """
    Extract description from SKILL.md YAML frontmatter.

    Looks for:
    ---
    name: ...
    description: ...
    ---
    """
    try:
        content = skill_md_path.read_text(encoding="utf-8")

        # Check for YAML frontmatter
        if not content.startswith("---"):
            return None

        # Find end of frontmatter
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return None

        frontmatter = content[3:end_idx]

        # Simple extraction without YAML parser dependency
        for line in frontmatter.split("\n"):
            line = line.strip()
            if line.startswith("description:"):
                desc = line[len("description:"):].strip()
                # Remove quotes if present
                if desc.startswith('"') and desc.endswith('"'):
                    desc = desc[1:-1]
                elif desc.startswith("'") and desc.endswith("'"):
                    desc = desc[1:-1]
                return desc

        return None

    except Exception:
        return None
def find_skills(repo_root: Path) -> List[Dict]:
    """
    Scan repository for all skills (folders containing SKILL.md).

    Returns list of skill dictionaries with metadata.
    """
    skills = []

    for domain_dir, domain_info in SKILL_DOMAINS.items():
        domain_path = repo_root / domain_dir

        if not domain_path.exists():
            continue

        # Find all subdirectories with SKILL.md
        for skill_path in domain_path.iterdir():
            if not skill_path.is_dir():
                continue

            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue

            # Extract skill name and description from SKILL.md
            skill_name = skill_path.name
            description = extract_skill_description(skill_md)

            # Calculate relative path from .codex/skills/ to skill folder
            relative_path = f"../../{domain_dir}/{skill_name}"

            skills.append({
                "name": skill_name,
                "source": relative_path,
                "source_absolute": str(skill_path.relative_to(repo_root)),
                "category": domain_info["category"],
                "description": description or f"Skill from {domain_dir}"
            })

    # Sort by category then name for consistent output
    skills.sort(key=lambda s: (s["category"], s["name"]))

    return skills

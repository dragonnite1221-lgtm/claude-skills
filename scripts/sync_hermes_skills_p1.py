# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_hermes_skills_base import *  # noqa: F403,E402


REPO_ROOT = Path(__file__).resolve().parent.parent
HERMES_SKILLS_DIR = Path.home() / ".hermes" / "skills"
TARGET_SUBDIR = "claude-skills"  # namespace to avoid collisions with Hermes built-in skills
DOMAIN_DIRS = [
    "engineering",
    "engineering-team",
    "product-team",
    "marketing-skill",
    "c-level-advisor",
    "project-management",
    "ra-qm-team",
    "business-growth",
    "finance",
]
def discover_skills(repo_root, domains=None):
    """Find all skills across specified domains."""
    skills = []
    search_domains = domains or DOMAIN_DIRS
    for domain in search_domains:
        domain_path = repo_root / domain
        if not domain_path.is_dir():
            continue
        for skill_dir in sorted(domain_path.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skills.append({
                    "domain": domain,
                    "name": skill_dir.name,
                    "source": skill_dir,
                    "skill_md": skill_md,
                })
    return skills
def read_frontmatter(skill_md):
    """Extract name and description from SKILL.md frontmatter."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end < 0:
            return {}
        fm = {}
        for line in text[3:end].splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip().strip("'\"")
        return fm
    except Exception:
        return {}
def sync_skill(skill, target_root, use_copy, verbose, dry_run):
    """Create a symlink or copy for one skill."""
    target = target_root / skill["domain"] / skill["name"]

    if target.exists() or target.is_symlink():
        if verbose:
            print(f"  skip (exists): {skill['domain']}/{skill['name']}")
        return "skip"

    if dry_run:
        if verbose:
            print(f"  would {'copy' if use_copy else 'link'}: {skill['domain']}/{skill['name']}")
        return "would"

    target.parent.mkdir(parents=True, exist_ok=True)

    if use_copy:
        shutil.copytree(skill["source"], target, dirs_exist_ok=True)
    else:
        target.symlink_to(skill["source"])

    if verbose:
        print(f"  {'copied' if use_copy else 'linked'}: {skill['domain']}/{skill['name']}")
    return "new"
def write_index(target_root, skills):
    """Write a skills-index.json for quick lookup."""
    index = {
        "source": "claude-code-skills",
        "total_skills": len(skills),
        "domains": {},
    }
    for s in skills:
        d = s["domain"]
        if d not in index["domains"]:
            index["domains"][d] = []
        fm = read_frontmatter(s["skill_md"])
        index["domains"][d].append({
            "name": s["name"],
            "description": fm.get("description", ""),
            "path": f"{d}/{s['name']}",
        })
    index_path = target_root / "skills-index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index_path

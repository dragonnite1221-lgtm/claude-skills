# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_codex_skills_base import *  # noqa: F403,E402
# fmt: off
from sync_codex_skills_p1 import SKILL_DOMAINS  # noqa: E402,E501
# fmt: on


def create_symlinks(repo_root: Path, skills: List[Dict], dry_run: bool = False, verbose: bool = False) -> Dict:
    """
    Create symlinks in .codex/skills/ directory.

    Returns summary of operations.
    """
    codex_skills_dir = repo_root / ".codex" / "skills"

    created = []
    updated = []
    unchanged = []
    errors = []

    if not dry_run:
        codex_skills_dir.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        symlink_path = codex_skills_dir / skill["name"]
        target = skill["source"]

        try:
            if symlink_path.is_symlink():
                current_target = os.readlink(symlink_path)
                if current_target == target:
                    unchanged.append(skill["name"])
                    if verbose:
                        print(f"  [UNCHANGED] {skill['name']} -> {target}")
                else:
                    if not dry_run:
                        symlink_path.unlink()
                        symlink_path.symlink_to(target)
                    updated.append(skill["name"])
                    if verbose:
                        print(f"  [UPDATED] {skill['name']} -> {target} (was: {current_target})")
            elif symlink_path.exists():
                errors.append(f"{skill['name']}: path exists but is not a symlink")
                if verbose:
                    print(f"  [ERROR] {skill['name']}: path exists but is not a symlink")
            else:
                if not dry_run:
                    symlink_path.symlink_to(target)
                created.append(skill["name"])
                if verbose:
                    print(f"  [CREATED] {skill['name']} -> {target}")

        except Exception as e:
            errors.append(f"{skill['name']}: {str(e)}")
            if verbose:
                print(f"  [ERROR] {skill['name']}: {str(e)}")

    return {
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "errors": errors
    }
def generate_skills_index(repo_root: Path, skills: List[Dict], dry_run: bool = False) -> Dict:
    """
    Generate .codex/skills-index.json manifest.

    Returns the index data.
    """
    # Calculate category counts
    categories = {}
    for skill in skills:
        cat = skill["category"]
        if cat not in categories:
            # Find domain info
            for domain_dir, domain_info in SKILL_DOMAINS.items():
                if domain_info["category"] == cat:
                    categories[cat] = {
                        "count": 0,
                        "source": f"../../{domain_dir}",
                        "description": domain_info["description"]
                    }
                    break
        if cat in categories:
            categories[cat]["count"] += 1

    # Build index
    index = {
        "version": "1.0.0",
        "name": "claude-code-skills",
        "description": "Production-ready skill packages for AI agents - Marketing, Engineering, Product, C-Level, PM, and RA/QM",
        "repository": "https://github.com/alirezarezvani/claude-skills",
        "total_skills": len(skills),
        "skills": [
            {
                "name": s["name"],
                "source": s["source"],
                "category": s["category"],
                "description": s["description"]
            }
            for s in skills
        ],
        "categories": categories
    }

    if not dry_run:
        index_path = repo_root / ".codex" / "skills-index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    return index
def validate_symlinks(repo_root: Path, skills: List[Dict]) -> List[str]:
    """
    Validate that all symlinks resolve to valid SKILL.md files.

    Returns list of broken symlinks.
    """
    broken = []
    codex_skills_dir = repo_root / ".codex" / "skills"

    for skill in skills:
        symlink_path = codex_skills_dir / skill["name"]

        if not symlink_path.exists():
            broken.append(f"{skill['name']}: symlink does not exist")
            continue

        skill_md = symlink_path / "SKILL.md"
        if not skill_md.exists():
            broken.append(f"{skill['name']}: SKILL.md not found through symlink")

    return broken

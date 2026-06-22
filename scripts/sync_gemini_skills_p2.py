# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sync_gemini_skills_base import *  # noqa: F403,E402
# fmt: off
from sync_gemini_skills_p1 import find_skills  # noqa: E402,E501
# fmt: on


def create_symlinks(repo_root: Path, skills: List[Dict], dry_run: bool = False, verbose: bool = False) -> Dict:
    """
    Create symlinks in .gemini/skills/ directory.
    """
    gemini_skills_dir = repo_root / ".gemini" / "skills"
    
    created, updated, unchanged, removed_stale, errors = [], [], [], [], []

    if not dry_run:
        gemini_skills_dir.mkdir(parents=True, exist_ok=True)

    expected_names = {skill["name"] for skill in skills}
    if gemini_skills_dir.exists():
        for existing_dir in gemini_skills_dir.iterdir():
            if existing_dir.name in expected_names:
                continue
            symlink_path = existing_dir / "SKILL.md"
            if existing_dir.is_dir() and symlink_path.is_symlink():
                if not dry_run:
                    shutil.rmtree(existing_dir)
                removed_stale.append(existing_dir.name)

    for skill in skills:
        skill_name = skill["name"]
        skill_dest_dir = gemini_skills_dir / skill_name
        
        if not dry_run:
            skill_dest_dir.mkdir(exist_ok=True)
            
        symlink_path = skill_dest_dir / "SKILL.md"
        target = skill["source"]

        try:
            if symlink_path.is_symlink():
                current_target = os.readlink(symlink_path)
                if current_target == target:
                    unchanged.append(skill_name)
                else:
                    if not dry_run:
                        symlink_path.unlink()
                        symlink_path.symlink_to(target)
                    updated.append(skill_name)
            elif symlink_path.exists():
                errors.append(f"{skill_name}: path exists but is not a symlink")
            else:
                if not dry_run:
                    symlink_path.symlink_to(target)
                created.append(skill_name)
        except Exception as e:
            errors.append(f"{skill_name}: {str(e)}")

    return {
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "removed_stale": removed_stale,
        "errors": errors,
    }
def generate_skills_index(repo_root: Path, skills: List[Dict], dry_run: bool = False) -> Dict:
    """
    Generate .gemini/skills-index.json manifest.
    """
    categories = {}
    for skill in skills:
        cat = skill["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "description": f"{cat.capitalize()} resources"}
        categories[cat]["count"] += 1

    index = {
        "version": "1.0.0",
        "name": "gemini-cli-skills",
        "total_skills": len(skills),
        "skills": [{"name": s["name"], "category": s["category"], "description": s["description"]} for s in skills],
        "categories": categories
    }

    if not dry_run:
        index_path = repo_root / ".gemini" / "skills-index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    return index
def main():
    parser = argparse.ArgumentParser(description="Sync Gemini skills")
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    skills = find_skills(repo_root)
    
    if not skills:
        print("No skills found.")
        sys.exit(1)

    symlink_results = create_symlinks(repo_root, skills, args.dry_run, args.verbose)
    generate_skills_index(repo_root, skills, args.dry_run)

    print(f"Total skills synced for Gemini CLI: {len(skills)}")
    print(f"Created: {len(symlink_results['created'])}")
    print(f"Updated: {len(symlink_results['updated'])}")
    print(f"Unchanged: {len(symlink_results['unchanged'])}")
    print(f"Removed stale: {len(symlink_results['removed_stale'])}")

    if symlink_results['errors']:
        print(f"Errors: {len(symlink_results['errors'])}")
        for error in symlink_results['errors']:
            print(f"  - {error}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Sync Gemini Skills - Generate symlinks and index for Gemini CLI compatibility.

This script scans the skill domains for SKILL.md files and creates:
1. Symlinks in .gemini/skills/ directory
2. skills-index.json manifest for tooling

Usage:
    python scripts/sync-gemini-skills.py [--dry-run] [--verbose]
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


# Domain mapping for categories based on top-level folder
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

if __name__ == "__main__":
    main()

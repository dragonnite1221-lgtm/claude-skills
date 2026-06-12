#!/usr/bin/env python3
"""Count repository items that are commonly referenced in docs."""

import argparse
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path


def load_gemini_sync_module(repo_root: Path):
    script_path = repo_root / "scripts" / "sync-gemini-skills.py"
    spec = importlib.util.spec_from_file_location("sync_gemini_skills", script_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_ls_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def collect_counts(repo_root: Path) -> dict:
    sync_module = load_gemini_sync_module(repo_root)
    skills = sync_module.find_skills(repo_root)
    tracked = git_ls_files(repo_root)

    categories = Counter(skill["category"] for skill in skills)
    gemini_mirror = list((repo_root / ".gemini" / "skills").glob("*/SKILL.md"))

    return {
        "skills": {
            "total": len(skills),
            "by_category": dict(sorted(categories.items())),
        },
        "gemini_mirror_skill_links": len(gemini_mirror),
        "python_tools_tracked": sum(1 for path in tracked if path.endswith(".py")),
        "agents_markdown_tracked": sum(
            1 for path in tracked if path.startswith("agents/") and path.endswith(".md")
        ),
        "commands_markdown_tracked": sum(
            1 for path in tracked if path.startswith("commands/") and path.endswith(".md")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Count repository inventory items")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root to inspect",
    )
    args = parser.parse_args()
    print(json.dumps(collect_counts(args.repo_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

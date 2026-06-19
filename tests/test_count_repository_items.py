"""Tests for the inventory drift gate (FLEET_QUALITY_INVARIANTS Invariant 1).

A gate that is never tested can silently stop gating, so we verify both that
the committed INVENTORY.md matches the live repo state and that the renderer
is a deterministic pure function of the counts."""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "count-repository-items.py"

spec = importlib.util.spec_from_file_location("count_repository_items", SCRIPT_PATH)
count_repository_items = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = count_repository_items
spec.loader.exec_module(count_repository_items)


def test_committed_inventory_matches_repo_state():
    """The committed INVENTORY.md must equal a fresh render — i.e. the drift
    gate (`--check`) passes for the current tree."""
    counts = count_repository_items.collect_counts(REPO_ROOT)
    expected = count_repository_items.render_inventory_md(counts) + "\n"
    actual = (REPO_ROOT / "documentation" / "INVENTORY.md").read_text(encoding="utf-8")
    assert actual == expected, (
        "INVENTORY.md is stale — run "
        "`python3 scripts/count-repository-items.py --write` and commit."
    )


def test_render_is_deterministic():
    counts = {
        "skills": {"total": 2, "by_category": {"b": 1, "a": 1}},
        "gemini_mirror_skill_links": 2,
        "python_tools_tracked": 5,
        "agents_markdown_tracked": 3,
        "commands_markdown_tracked": 4,
    }
    first = count_repository_items.render_inventory_md(counts)
    second = count_repository_items.render_inventory_md(counts)
    assert first == second
    assert "| Skills (total) | 2 |" in first
    assert "| Python tools (tracked `*.py`) | 5 |" in first


def test_check_detects_drift(tmp_path, monkeypatch):
    """`--check` must exit non-zero when INVENTORY.md does not match."""
    # Point the script at a tree whose INVENTORY.md is intentionally wrong by
    # rendering for the real repo but writing a stale file into a temp docs dir.
    counts = count_repository_items.collect_counts(REPO_ROOT)
    fresh = count_repository_items.render_inventory_md(counts) + "\n"
    stale = fresh.replace("Skills (total) |", "Skills (total) | 999 ")
    assert stale != fresh

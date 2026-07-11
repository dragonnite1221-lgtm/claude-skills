"""Regression tests for non-destructive experiment rollback."""

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_experiment.py"
SPEC = importlib.util.spec_from_file_location("run_experiment", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_safe_rollback_uses_revert_not_reset(monkeypatch, tmp_path):
    calls = []

    def fake_run_git(args, cwd=None, timeout=30):
        calls.append(args)
        return 0, "", ""

    monkeypatch.setattr(MODULE, "get_current_commit", lambda _path: "abc1234")
    monkeypatch.setattr(MODULE, "working_tree_changes", lambda _path: [])
    monkeypatch.setattr(MODULE, "run_git", fake_run_git)

    assert MODULE.safe_rollback(tmp_path, "abc1234", "test") is True
    assert ["revert", "--no-edit", "abc1234"] in calls
    assert not any("reset" in call for call in calls)


def test_safe_rollback_refuses_dirty_tracked_worktree(monkeypatch, tmp_path):
    monkeypatch.setattr(MODULE, "get_current_commit", lambda _path: "abc1234")
    monkeypatch.setattr(MODULE, "working_tree_changes", lambda _path: [" M user.py"])
    calls = []
    monkeypatch.setattr(MODULE, "run_git", lambda *args, **kwargs: calls.append(args))

    assert MODULE.safe_rollback(tmp_path, "abc1234", "test") is False
    assert calls == []


def test_failed_revert_is_aborted(monkeypatch, tmp_path):
    calls = []

    def fake_run_git(args, cwd=None, timeout=30):
        calls.append(args)
        if args[:2] == ["revert", "--no-edit"]:
            return 1, "", "conflict"
        return 0, "", ""

    monkeypatch.setattr(MODULE, "get_current_commit", lambda _path: "abc1234")
    monkeypatch.setattr(MODULE, "working_tree_changes", lambda _path: [])
    monkeypatch.setattr(MODULE, "run_git", fake_run_git)

    assert MODULE.safe_rollback(tmp_path, "abc1234", "test") is False
    assert calls[-1] == ["revert", "--abort"]

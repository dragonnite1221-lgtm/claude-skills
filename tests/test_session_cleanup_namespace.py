"""Cleanup must select only the requested session's exact branch namespace."""
import contextlib
import importlib.util
import io
from pathlib import Path
import types
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/agenthub/scripts/session_manager.py"
SPEC = importlib.util.spec_from_file_location("session_cleanup_namespace", SCRIPT)
SESSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SESSION)
SID = "20260317-143022"


def porcelain(records):
    return "\n\n".join(f"worktree {path}\nHEAD {'a' * 40}\n{ref}" for path, ref in records)


class CleanupNamespaceTests(unittest.TestCase):
    def cleanup(self, records, session_id=SID, returncode=0):
        output = io.StringIO()
        # Every Git entry point is mocked, including all removal subprocesses.
        with patch.object(SESSION, "load_config", return_value={"task": "fixture"}), \
                patch.object(SESSION, "run_git", return_value=porcelain(records)) as listing, \
                patch.object(SESSION.subprocess, "run", return_value=types.SimpleNamespace(returncode=returncode)) as remove, \
                contextlib.redirect_stdout(output):
            SESSION.cleanup_session(session_id)
        listing.assert_called_once_with("worktree", "list", "--porcelain")
        calls = [call.args[0] for call in remove.call_args_list]
        for call in calls:
            self.assertEqual(call[:4], ["git", "worktree", "remove", "--force"])
        return [call[-1] for call in calls], output.getvalue()

    def test_exact_session_branches_are_selected(self):
        records = [("/fixture/one", f"branch refs/heads/hub/{SID}/agent-1/attempt-1"),
                   ("/fixture/two", f"branch refs/heads/hub/{SID}/agent-2/attempt-2")]
        targets, output = self.cleanup(records)
        self.assertEqual(targets, ["/fixture/one", "/fixture/two"])
        self.assertIn("Cleaned up 2 worktrees", output)

    def test_similar_and_nested_namespaces_are_not_selected(self):
        refs = [f"refs/heads/backup/hub/{SID}/keep", f"refs/heads/myhub/{SID}/keep",
                f"refs/heads/not-hub/{SID}/keep", f"refs/remotes/hub/{SID}/keep",
                f"refs/heads/hub/{SID}-other/keep", f"refs/heads/hub/prefix-{SID}/keep"]
        records = [(f"/fixture/{i}", "branch " + ref) for i, ref in enumerate(refs)]
        self.assertEqual(self.cleanup(records)[0], [])

    def test_mixed_records_preserve_unrelated_worktrees(self):
        records = [("/fixture/backup", f"branch refs/heads/backup/hub/{SID}/keep"),
                   ("/fixture/target", f"branch refs/heads/hub/{SID}/agent-1/attempt-1"),
                   ("/fixture/other", "branch refs/heads/hub/other-session/agent-1/attempt-1")]
        self.assertEqual(self.cleanup(records)[0], ["/fixture/target"])

    def test_detached_and_main_worktrees_are_ignored(self):
        records = [("/fixture/main", "branch refs/heads/main"), ("/fixture/detached", "detached"),
                   ("/fixture/bare", "bare")]
        self.assertEqual(self.cleanup(records)[0], [])

    def test_paths_with_spaces_and_unicode_are_preserved(self):
        path = "/fixture/한글 worktree"
        self.assertEqual(self.cleanup([(path, f"branch refs/heads/hub/{SID}/agent-1/attempt-1")])[0], [path])

    def test_session_ids_are_matched_literally(self):
        sid = "research.v1"
        records = [("/fixture/target", f"branch refs/heads/hub/{sid}/agent-1/attempt-1"),
                   ("/fixture/other", "branch refs/heads/hub/researchXv1/agent-1/attempt-1")]
        self.assertEqual(self.cleanup(records, session_id=sid)[0], ["/fixture/target"])

    def test_empty_listing_is_a_noop(self):
        targets, output = self.cleanup([])
        self.assertEqual(targets, [])
        self.assertIn("Cleaned up 0 worktrees", output)

    def test_unsuccessful_mock_removal_is_not_counted(self):
        targets, output = self.cleanup([("/fixture/target", f"branch refs/heads/hub/{SID}/agent-1")], returncode=1)
        self.assertEqual(targets, ["/fixture/target"])
        self.assertIn("Cleaned up 0 worktrees", output)
        self.assertNotIn("Removed worktree:", output)


if __name__ == "__main__":
    unittest.main()

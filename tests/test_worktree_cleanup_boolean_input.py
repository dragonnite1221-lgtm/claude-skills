"""Reject string booleans before worktree cleanup can run git."""

import argparse
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/git-worktree-manager/scripts/worktree_cleanup.py"
SPEC = importlib.util.spec_from_file_location("worktree_cleanup", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BooleanInputTest(unittest.TestCase):
    def test_string_false_never_reaches_git(self):
        args = argparse.Namespace(input=None, repo=".", stale_days=14, base_branch="main", remove_merged=False, force=False, format="json")
        for key in ("remove_merged", "force"):
            with self.subTest(key=key):
                with patch.object(MODULE, "parse_args", return_value=args), patch.object(MODULE, "load_json_input", return_value={key: "false"}), patch.object(MODULE, "run") as run:
                    with self.assertRaises(MODULE.CLIError):
                        MODULE.main()
                    run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

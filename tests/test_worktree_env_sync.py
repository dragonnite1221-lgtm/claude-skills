"""Environment sync must not overwrite files behind worktree links."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/git-worktree-manager/scripts/worktree_manager.py"
SPEC = importlib.util.spec_from_file_location("worktree_manager", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorktreeEnvSyncTest(unittest.TestCase):
    def test_linked_destination_does_not_change_external_file(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            src, dst = root / "src", root / "dst"
            src.mkdir()
            dst.mkdir()
            (src / ".env").write_text("new", encoding="utf-8")
            outside = root / "outside"
            outside.write_text("keep", encoding="utf-8")
            (dst / ".env").symlink_to(outside)
            with self.assertRaises(MODULE.CLIError):
                MODULE.sync_env_files(src, dst)
            self.assertEqual(outside.read_text(encoding="utf-8"), "keep")
            self.assertTrue((dst / ".env").is_symlink())

    def test_copy_failure_preserves_previous_environment(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            src, dst = root / "src", root / "dst"
            src.mkdir()
            dst.mkdir()
            (src / ".env").write_text("new", encoding="utf-8")
            (dst / ".env").write_text("keep", encoding="utf-8")
            with patch.object(MODULE.shutil, "copy2", side_effect=OSError("copy failed")):
                with self.assertRaises(OSError):
                    MODULE.sync_env_files(src, dst)
            self.assertEqual((dst / ".env").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()

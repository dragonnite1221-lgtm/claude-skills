"""Wiki writers must not change targets of imported links."""

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "engineering/llm-wiki/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WikiWriteBoundaryTest(unittest.TestCase):
    def test_log_symlink_preserves_external_file(self):
        script = load("append_log")
        with tempfile.TemporaryDirectory() as root:
            vault = Path(root) / "vault"
            (vault / "wiki").mkdir(parents=True)
            outside = Path(root) / "outside.md"
            outside.write_text("keep", encoding="utf-8")
            (vault / "wiki/log.md").symlink_to(outside)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                script.append_log(vault, "note", "test", None)
            self.assertEqual(outside.read_text(encoding="utf-8"), "keep")

    def test_index_symlink_preserves_external_file(self):
        script = load("update_index")
        with tempfile.TemporaryDirectory() as root:
            vault = Path(root) / "vault"
            (vault / "wiki").mkdir(parents=True)
            outside = Path(root) / "raw.md"
            outside.write_text("keep", encoding="utf-8")
            (vault / "wiki/index.md").symlink_to(outside)
            with patch.object(sys, "argv", ["update_index.py", "--vault", str(vault)]), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                script.main()
            self.assertEqual(outside.read_text(encoding="utf-8"), "keep")

    def test_index_replacement_failure_preserves_previous_file(self):
        script = load("update_index")
        with tempfile.TemporaryDirectory() as root:
            vault = Path(root) / "vault"
            (vault / "wiki").mkdir(parents=True)
            index = vault / "wiki/index.md"
            index.write_text("keep", encoding="utf-8")
            with patch.object(sys, "argv", ["update_index.py", "--vault", str(vault)]), patch.object(script.os, "replace", side_effect=OSError("failed")), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                script.main()
            self.assertEqual(index.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()

"""Required vault templates must be installed before reporting success."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/llm-wiki/scripts/init_vault.py"
SPEC = importlib.util.spec_from_file_location("vault_required_templates", SCRIPT)
INIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INIT)


class RequiredTemplatesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vault = self.root / "vault"

    def assert_required_failure(self, tool="codex", as_json=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as raised:
                INIT.init_vault(self.vault, "Topic", tool, True, as_json)
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("[warn]", err.getvalue())
        if as_json:
            self.assertEqual(json.loads(out.getvalue())["status"], "error")
        else:
            self.assertIn("[error]", err.getvalue())
            self.assertNotIn("[ok]", out.getvalue())

    def test_selected_schema_directory_is_an_error(self):
        (self.vault / "AGENTS.md").mkdir(parents=True)
        self.assert_required_failure()
        self.assertTrue((self.vault / "AGENTS.md").is_dir())

    def test_index_and_log_write_failures_are_errors(self):
        for name in ["index.md", "log.md"]:
            with self.subTest(name=name):
                self.vault = self.root / name
                (self.vault / "wiki" / name).mkdir(parents=True)
                self.assert_required_failure()

    def test_missing_required_assets_are_an_error(self):
        with patch.object(INIT, "ASSETS_DIR", self.root / "missing-assets"):
            self.assert_required_failure()

    def test_human_failure_does_not_report_success(self):
        (self.vault / "AGENTS.md").mkdir(parents=True)
        self.assert_required_failure(as_json=False)

    def test_all_tool_modes_succeed(self):
        for tool in INIT.TOOL_FILES:
            with self.subTest(tool=tool), contextlib.redirect_stdout(io.StringIO()):
                vault = self.root / tool
                result = INIT.init_vault(vault, "Topic", tool, False, True)
                self.assertEqual(result["status"], "ok")
                self.assertEqual(len(result["installed_files"]), len(INIT.TOOL_FILES[tool]) + 2)
                self.assertTrue(all((vault / f).is_file() for f in result["installed_files"]))

    def test_optional_reference_templates_remain_optional(self):
        assets = self.root / "minimal-assets"
        assets.mkdir()
        for name in ["AGENTS.md.template", "index.md.template", "log.md.template"]:
            (assets / name).write_bytes((INIT.ASSETS_DIR / name).read_bytes())
        with patch.object(INIT, "ASSETS_DIR", assets), contextlib.redirect_stdout(io.StringIO()):
            result = INIT.init_vault(self.vault, "Topic", "codex", False, True)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["page_templates_copied"], 0)

    def test_failed_init_preserves_unrelated_user_files(self):
        (self.vault / "raw").mkdir(parents=True)
        source = self.vault / "raw/user.txt"
        source.write_bytes(b"Original user content\x00")
        before = (source.read_bytes(), source.stat().st_mtime_ns)
        (self.vault / "AGENTS.md").mkdir()
        self.assert_required_failure()
        self.assertEqual((source.read_bytes(), source.stat().st_mtime_ns), before)

    def test_failed_cli_returns_nonzero_json_and_human(self):
        for index, flags in enumerate([["--json"], []]):
            vault = self.root / str(index)
            (vault / "AGENTS.md").mkdir(parents=True)
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--path", str(vault), "--topic", "Topic", "--tool", "codex", "--force", *flags], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            if flags:
                self.assertEqual(json.loads(result.stdout)["status"], "error")
            else:
                self.assertIn("[error]", result.stderr)
                self.assertNotIn("[ok]", result.stdout)


if __name__ == "__main__":
    unittest.main()

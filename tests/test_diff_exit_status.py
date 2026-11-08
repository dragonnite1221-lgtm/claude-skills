"""Diff noise and Git failures must not produce success exit statuses."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/karpathy-coder/scripts/diff_surgeon.py"
HEADER = "diff --git a/sample.py b/sample.py\n--- a/sample.py\n+++ b/sample.py\n@@ -0,0 +1 @@\n"


class ExitStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              cwd=self.root, capture_output=True, text=True)

    def assert_patch(self, lines, verdict, exit_code, ratio=None):
        patch = self.root / "change.diff"
        patch.write_text(HEADER + lines if lines else "", encoding="utf-8")
        for options in ((), ("--json",)):
            with self.subTest(options=options):
                result = self.run_cli("--file", str(patch), *options)
                self.assertEqual(exit_code, result.returncode, result.stderr)
                self.assertEqual("", result.stderr)
                if options:
                    data = json.loads(result.stdout)
                    self.assertEqual(verdict, data["verdict"])
                    if ratio is not None:
                        self.assertEqual(ratio, data["noise_ratio"])
                elif lines:
                    self.assertIn(f"Verdict: {verdict}", result.stdout)
                else:
                    self.assertIn("No diff to analyze", result.stdout)

    def test_clean_patch(self):
        self.assert_patch("+value = 1\n", "CLEAN", 0, 0.0)

    def test_noisy_patch(self):
        self.assert_patch("+# note\n+a = 1\n+b = 2\n+c = 3\n+d = 4\n",
                          "NOISY", 1, 0.2)

    def test_very_noisy_patch(self):
        self.assert_patch("+# note\n", "VERY_NOISY", 1, 1.0)

    def test_empty_patch(self):
        self.assert_patch("", "CLEAN", 0)

    def test_git_failure_outside_repository(self):
        result = self.run_cli("--json")
        self.assertEqual(1, result.returncode)
        self.assertIn("[error] git diff failed:", result.stderr)
        self.assertNotIn("CLEAN", result.stdout)

    def test_git_failure_for_bad_revision(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True,
                       capture_output=True, text=True)
        result = self.run_cli("--diff", "missing-revision..HEAD")
        self.assertEqual(1, result.returncode)
        self.assertIn("[error] git diff failed:", result.stderr)
        self.assertNotIn("No diff to analyze", result.stdout)

    def test_empty_staged_diff_still_succeeds(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True,
                       capture_output=True, text=True)
        result = self.run_cli("--json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual("CLEAN", json.loads(result.stdout)["verdict"])

    def test_help(self):
        result = self.run_cli("--help")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--json", result.stdout)


if __name__ == "__main__":
    unittest.main()

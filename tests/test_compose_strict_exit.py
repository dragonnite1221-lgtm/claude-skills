"""CLI regressions for the documented Compose strict-mode exit contract."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/docker-development/scripts/compose_validator.py"
CLEAN = """services:
  app:
    image: app:1
    healthcheck:
      test: [CMD, true]
    restart: always
    mem_limit: 256m
"""


class ComposeStrictExitTests(unittest.TestCase):
    def run_report(self, content, strict, output="json"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "compose.yml"
            path.write_text(content, encoding="utf-8")
            command = [sys.executable, str(SCRIPT), str(path), "--output", output]
            if strict:
                command.append("--strict")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(path.read_text(encoding="utf-8"), content)
        self.assertEqual(result.stderr, "")
        return result

    def test_strict_clean_succeeds(self):
        result = self.run_report(CLEAN, True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["findings"], [])

    def test_strict_low_warning_fails(self):
        result = self.run_report(CLEAN + "version: '3.8'\n", True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["low"], 1)

    def test_strict_high_finding_fails(self):
        result = self.run_report(CLEAN.replace("app:1", "app:latest"), True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["high"], 1)

    def test_strict_critical_uses_error_status(self):
        result = self.run_report(CLEAN + "    environment:\n      SECRET_KEY: fixture\n", True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["critical"], 1)

    def test_non_strict_retains_success_with_findings(self):
        for content in (CLEAN + "version: '3.8'\n", CLEAN + "    environment:\n      SECRET_KEY: fixture\n"):
            with self.subTest(content=content):
                result = self.run_report(content, False)
                self.assertEqual(result.returncode, 0)
                self.assertTrue(json.loads(result.stdout)["findings"])

    def test_text_and_json_exit_codes_match(self):
        for content, expected in ((CLEAN, 0), (CLEAN + "version: '3.8'\n", 1),
                                  (CLEAN + "    environment:\n      SECRET_KEY: fixture\n", 2)):
            with self.subTest(expected=expected):
                result = self.run_report(content, True, "text")
                self.assertEqual(result.returncode, expected)
                self.assertIn("Docker Compose Validation Report", result.stdout)

    def test_strict_mode_still_elevates_resource_findings(self):
        content = CLEAN.replace("    mem_limit: 256m\n", "")
        normal = self.run_report(content, False)
        strict = self.run_report(content, True)
        self.assertEqual((normal.returncode, strict.returncode), (0, 1))
        self.assertEqual(json.loads(normal.stdout)["finding_counts"]["low"], 1)
        self.assertEqual(json.loads(strict.stdout)["finding_counts"]["medium"], 1)


if __name__ == "__main__":
    unittest.main()

"""CLI regressions for Helm values strict-mode exit status."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/helm-chart-builder/scripts/values_validator.py"
CLEAN = "replicaCount: 1 # Number of replicas\n"
WARNING = "replica_count: 1 # Number of replicas\n"
CRITICAL = "password: fixture-only # Synthetic example\n"


class HelmValuesStrictExitTests(unittest.TestCase):
    def run_report(self, content, strict, output="json"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "values.yaml"
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

    def test_strict_warning_fails(self):
        result = self.run_report(WARNING, True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["high"], 1)

    def test_strict_default_quality_fails(self):
        result = self.run_report("tag: latest # Image tag\n", True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["high"], 1)

    def test_strict_critical_uses_error_status(self):
        result = self.run_report(CRITICAL, True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["finding_counts"]["critical"], 1)

    def test_non_strict_retains_success_with_findings(self):
        for content in (WARNING, CRITICAL):
            with self.subTest(content=content):
                result = self.run_report(content, False)
                self.assertEqual(result.returncode, 0)
                self.assertTrue(json.loads(result.stdout)["findings"])

    def test_text_exit_codes_match_json(self):
        for content, expected in ((CLEAN, 0), (WARNING, 1), (CRITICAL, 2)):
            with self.subTest(expected=expected):
                result = self.run_report(content, True, "text")
                self.assertEqual(result.returncode, expected)
                self.assertIn("Values.yaml Validation Report", result.stdout)

    def test_strict_severity_elevation_is_retained(self):
        normal = self.run_report(WARNING, False)
        strict = self.run_report(WARNING, True)
        self.assertEqual((normal.returncode, strict.returncode), (0, 1))
        self.assertEqual(json.loads(normal.stdout)["finding_counts"]["medium"], 1)
        self.assertEqual(json.loads(strict.stdout)["finding_counts"]["high"], 1)

    def test_critical_takes_precedence_over_other_findings(self):
        result = self.run_report(WARNING + CRITICAL, True)
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report["finding_counts"]["high"], 1)
        self.assertEqual(report["finding_counts"]["critical"], 1)


if __name__ == "__main__":
    unittest.main()

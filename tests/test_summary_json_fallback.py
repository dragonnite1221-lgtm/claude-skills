"""CLI regression tests for the summary formatter's JSON fallback."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "product-team/research-summarizer/scripts/format_summary.py"
COUNTS = {"academic": 12, "article": 11, "report": 12, "executive": 6,
          "comparison": 7, "literature": 8}


class SummaryJsonFallbackTests(unittest.TestCase):
    def run_cli(self, *args):
        process = subprocess.run([sys.executable, "-B", str(SOURCE), *args],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        return process.stdout

    def assert_listing(self, text):
        payload = json.loads(text)
        self.assertIsInstance(payload, list)
        self.assertEqual([item["key"] for item in payload], list(COUNTS))
        self.assertEqual({item["key"]: item["sections"] for item in payload}, COUNTS)
        for item in payload:
            self.assertEqual(set(item), {"key", "name", "description", "sections"})

    def test_json_without_template(self):
        self.assert_listing(self.run_cli("--output", "json"))

    def test_short_json_option_without_template(self):
        self.assert_listing(self.run_cli("-o", "json"))

    def test_length_does_not_contaminate_fallback_json(self):
        for length in ["brief", "standard", "detailed"]:
            with self.subTest(length=length):
                self.assert_listing(self.run_cli("--length", length, "--output", "json"))

    def test_explicit_listing_matches_implicit_listing(self):
        explicit = self.run_cli("--list-templates", "--output", "json")
        self.assertEqual(explicit, self.run_cli("--output", "json"))

    def test_default_text_keeps_guidance(self):
        text = self.run_cli()
        self.assertTrue(text.startswith("No template specified. Available templates:\n\n"))
        self.assertIn("Available Summary Templates", text)
        self.assertTrue(text.endswith("\nUsage: python scripts/format_summary.py --template academic\n"))

    def test_all_explicit_templates_and_lengths_remain_objects(self):
        for template, count in COUNTS.items():
            for length in ["brief", "standard", "detailed"]:
                with self.subTest(template=template, length=length):
                    payload = json.loads(self.run_cli("--template", template, "--length", length,
                                                      "--output", "json"))
                    self.assertEqual(payload["template"], template)
                    self.assertEqual(payload["length"], length)
                    self.assertEqual(len(payload["sections"]), 4 if length == "brief" else count)

    def test_explicit_listing_still_takes_precedence(self):
        self.assert_listing(self.run_cli("--list-templates", "--template", "academic", "-o", "json"))

    def test_help_still_succeeds(self):
        text = self.run_cli("--help")
        self.assertIn("--list-templates", text)
        self.assertIn("--output", text)


if __name__ == "__main__":
    unittest.main()

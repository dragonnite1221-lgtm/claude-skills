"""A present, empty meta description must not consume the following field."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/content-production/scripts/content_quality_gates.py"
SPEC = importlib.util.spec_from_file_location("content_quality_gates", SCRIPT)
GATES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATES)


def article():
    return ("---\ndescription:\nsummary: " + "x" * 146
            + "\nupdated: 2026-11-08\n---\n\n# " + "T" * 55
            + "\n\nUseful article text.")


class EmptyMetaDescriptionTests(unittest.TestCase):
    def assert_empty(self, text):
        result = GATES.check_meta_description(text)
        self.assertFalse(result["passed"])
        self.assertEqual(result["findings"],
                         ["Meta description too short: 0 chars (aim for 150-160)."])

    def test_empty_value_at_end(self):
        self.assert_empty("description:")

    def test_empty_quoted_or_whitespace_values(self):
        for value in ("", " ", "\t", '""', "''", '"   "', "'\t'"):
            with self.subTest(value=value):
                self.assert_empty("description: " + value)

    def test_next_field_never_becomes_description(self):
        for ending in ("\n", "\r\n"):
            for blank in ("", ending):
                text = "description:" + ending + blank + "summary: " + "x" * 146
                with self.subTest(ending=ending, blank=blank):
                    self.assert_empty(text)

    def test_valid_description_lengths(self):
        for length in (150, 155, 160):
            for quote in ("", "'", '"'):
                for ending in ("", "\nupdated: 2026", "\r\nupdated: 2026"):
                    for spacing in ("", " ", "\t", "\u00a0", "\f", "\v"):
                        text = "description:" + spacing + quote + "x" * length + quote + spacing + ending
                        with self.subTest(length=length, quote=quote, ending=ending, spacing=spacing):
                            self.assertTrue(GATES.check_meta_description(text)["passed"])

    def test_outside_lengths_still_fail(self):
        for length in (1, 149, 161, 300):
            with self.subTest(length=length):
                self.assertFalse(GATES.check_meta_description("description: " + "x" * length)["passed"])

    def test_absent_description_remains_optional(self):
        result = GATES.check_meta_description("# A title\n\nArticle text.")
        self.assertEqual(result, {"gate": "meta-description", "passed": True, "findings": []})

    def test_empty_description_prevents_publish_verdict(self):
        result = GATES.run_gates(article())
        self.assertEqual(result["gates_passed"], 7)
        self.assertEqual(result["verdict"], "TARGET")
        self.assertEqual([r["gate"] for r in result["results"] if not r["passed"]],
                         ["meta-description"])

    def test_cli_json_and_human_report_empty_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.md"
            path.write_text(article(), encoding="utf-8")
            for flags in ([], ["--json"]):
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path), *flags],
                                        capture_output=True, text=True)
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                if flags:
                    self.assertEqual(json.loads(result.stdout), GATES.run_gates(article()))
                else:
                    self.assertIn("Verdict: TARGET", result.stdout)
                    self.assertIn("Meta description too short: 0 chars", result.stdout)


if __name__ == "__main__":
    unittest.main()

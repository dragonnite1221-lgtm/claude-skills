"""Regression checks for SEO analysis of empty drafts."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / (
    "marketing-skill/content-production/scripts/seo_optimizer.py"
)
SPEC = importlib.util.spec_from_file_location("seo_optimizer", SCRIPT)
SEO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEO)


class EmptyContentTests(unittest.TestCase):
    def test_empty_readability_has_complete_metrics(self):
        result = SEO.SEOOptimizer().analyze("")
        self.assertEqual(result["readability"], {
            "score": 0, "level": "Unknown", "avg_sentence_length": 0,
        })

    def test_empty_draft_gets_actionable_recommendations(self):
        result = SEO.SEOOptimizer().analyze("")
        self.assertEqual(result["content_length"], 0)
        self.assertEqual(result["optimization_score"], 0)
        self.assertIn("Increase content length to at least 300 words (currently 0)",
                      result["recommendations"])
        self.assertNotIn("Simplify sentences for better readability",
                         result["recommendations"])

    def test_whitespace_only_drafts(self):
        for content in [" ", "\t\r\n", "\u00a0", "\u2003", "\u2028"]:
            with self.subTest(content=repr(content)):
                result = SEO.SEOOptimizer().analyze(content)
                self.assertEqual(result["readability"]["avg_sentence_length"], 0)
                self.assertEqual(result["optimization_score"], 0)

    def test_empty_draft_with_primary_and_secondary_keywords(self):
        result = SEO.SEOOptimizer().analyze("", "alpha", ["beta"])
        self.assertEqual(result["keyword_analysis"]["primary_keyword"]["count"], 0)
        self.assertEqual(result["keyword_analysis"]["secondary_keywords"][0]["count"], 0)
        self.assertIn("Include primary keyword in the first paragraph",
                      result["recommendations"])

    def test_formatter_handles_empty_draft(self):
        report = SEO.optimize_content("", "alpha", "beta,gamma")
        self.assertIn("Overall SEO Score: 0/100", report)
        self.assertIn("Readability: Unknown (Score: 0)", report)

    def test_nonempty_readability_remains_unchanged(self):
        result = SEO.SEOOptimizer().analyze("Alpha beta gamma")
        self.assertEqual(result["readability"], {
            "score": 90, "level": "Easy", "avg_sentence_length": 3.0,
        })

    def test_empty_and_whitespace_file_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.txt"
            for content, flags in [("", []), (" \t\n", ["--keyword", "alpha"]),
                                   ("", ["-k", "alpha", "-s", "beta,gamma"])]:
                path.write_text(content, encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path),
                                         *flags], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertIn("Readability: Unknown (Score: 0)", result.stdout)

    def test_long_sentences_still_get_readability_advice(self):
        result = SEO.SEOOptimizer().analyze(" ".join(["word"] * 25))
        self.assertEqual(result["readability"]["avg_sentence_length"], 25.0)
        self.assertIn("Simplify sentences for better readability",
                      result["recommendations"])


if __name__ == "__main__":
    unittest.main()

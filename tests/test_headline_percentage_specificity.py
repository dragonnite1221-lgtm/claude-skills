"""Percentage-specificity regression tests for the standalone headline scorer."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/copywriting/scripts/headline_scorer.py"
SPEC = importlib.util.spec_from_file_location("headline_scorer", SCRIPT)
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


class PercentageSpecificityTests(unittest.TestCase):
    def specificity(self, headline):
        return SCORER.score_specificity(headline, SCORER.tokenize(headline))

    def cli(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_percentage_at_end(self):
        self.assertEqual(self.specificity("Save 50%"),
                         (68, ["contains number", "percentage"]))

    def test_percentage_before_whitespace_or_punctuation(self):
        for suffix in (" today", "!", ".", ", now", ")", "\nnow", "\tnow", " — save"):
            with self.subTest(suffix=suffix):
                self.assertIn("percentage", self.specificity("Save 50%" + suffix)[1])

    def test_decimal_and_grouped_percentages(self):
        for number in ("0", "12.5", "0.25", "1,000", "100", "50.0"):
            with self.subTest(number=number):
                self.assertEqual(self.specificity("Save " + number + "%")[0], 68)

    def test_compact_percentage_remains_recognized(self):
        for suffix in ("off", "growth", "_gain", "2x"):
            with self.subTest(suffix=suffix):
                self.assertIn("percentage", self.specificity("50%" + suffix)[1])

    def test_non_percentage_controls(self):
        for headline in ("Save 50 dollars", "Save 50 percent", "A useful headline",
                         "Save % today", "Save 50 % today", "code50%"):
            with self.subTest(headline=headline):
                self.assertNotIn("percentage", self.specificity(headline)[1])

    def test_multiple_percentages_only_add_one_signal(self):
        score, signals = self.specificity("How to save 50% in 7 days and gain 25%")
        self.assertEqual(score, 100)
        self.assertEqual(signals.count("percentage"), 1)

    def test_single_headline_cli(self):
        headline = "Save 50% today"
        self.assertEqual(json.loads(self.cli(headline, "--json")),
                         [SCORER.score_headline(headline)])
        self.assertIn("percentage", self.cli(headline))
        self.assertEqual(SCORER.score_headline(headline)["overall_score"], 68)

    def test_file_cli(self):
        headlines = ["Save 50%", "Save 12.5% on your next purchase", "No discount"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "headlines.txt"
            path.write_text("\n".join(headlines), encoding="utf-8")
            self.assertEqual(json.loads(self.cli("--file", str(path), "--json")),
                             [SCORER.score_headline(h) for h in headlines])


if __name__ == "__main__":
    unittest.main()

"""Missing SEO keywords must not create matches or award keyword points."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/content-production/scripts/content_scorer.py"
SPEC = importlib.util.spec_from_file_location("content_scorer", SCRIPT)
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


class EmptySeoKeywordTests(unittest.TestCase):
    def assert_no_keyword(self, result):
        self.assertEqual(result["keyword_occurrences"], 0)
        self.assertEqual(result["keyword_density_pct"], 0)
        self.assertFalse(result["keyword_in_title"])
        self.assertFalse(result["keyword_in_intro"])

    def test_omitted_keyword_has_no_phantom_occurrences(self):
        result = SCORER.score_seo("alpha beta gamma")
        self.assert_no_keyword(result)
        self.assertEqual(result["score"], 0)

    def test_whitespace_only_keywords_are_absent(self):
        for keyword in (" ", "  ", "\t", "\n", "\r\n", "\u00a0", " \t\u2003\n"):
            with self.subTest(keyword=keyword):
                result = SCORER.score_seo("alpha beta gamma", "A clear title", keyword)
                self.assert_no_keyword(result)
                self.assertEqual(result["score"], 0)

    def test_empty_text_and_keyword(self):
        self.assert_no_keyword(SCORER.score_seo("", "", ""))

    def test_other_seo_points_are_preserved(self):
        result = SCORER.score_seo("## First\n## Second\n## Third", "T" * 40)
        self.assert_no_keyword(result)
        self.assertEqual(result["h2_count"], 3)
        self.assertEqual(result["score"], 8)

    def test_nonempty_single_keyword(self):
        result = SCORER.score_seo("alpha beta alpha", "Alpha guide", "ALPHA")
        self.assertEqual(result["keyword_occurrences"], 2)
        self.assertEqual(result["keyword_density_pct"], 66.67)
        self.assertEqual(result["score"], 14)

    def test_nonempty_phrase_and_existing_whitespace_policy(self):
        for keyword in ("alpha alpha", " alpha alpha "):
            result = SCORER.score_seo("alpha alpha alpha", "Guide", keyword)
            self.assertEqual(result["keyword_occurrences"], 2)
            self.assertEqual(result["keyword_density_pct"], 133.33)

    def test_aggregate_matches_component_scores(self):
        result = SCORER.score_content("alpha beta gamma", "A clear title", "")
        self.assert_no_keyword(result["sections"]["seo"])
        self.assertEqual(result["total_score"], sum(s["score"] for s in result["sections"].values()))

    def test_cli_optional_blank_keyword_and_additive_json(self):
        text = "# A clear title\n\nalpha beta gamma"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.md"
            path.write_text(text, encoding="utf-8")
            for keyword_args in ([], [""], [" "]):
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path),
                                         *keyword_args, "--json"], capture_output=True, text=True)
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                self.assertIn("CONTENT SCORER", result.stdout)
                payload = json.loads(result.stdout[result.stdout.index("\n{\n") + 1:])
                self.assert_no_keyword(payload["sections"]["seo"])
                expected = SCORER.score_content(text, "A clear title", keyword_args[0] if keyword_args else "")
                self.assertEqual(payload, expected)


if __name__ == "__main__":
    unittest.main()

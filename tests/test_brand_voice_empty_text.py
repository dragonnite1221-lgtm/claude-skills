"""Empty sentence analysis keeps a stable schema for both output formats."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/content-production/scripts/brand_voice_analyzer.py"
SPEC = importlib.util.spec_from_file_location("brand_voice", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BrandVoiceEmptyTextTests(unittest.TestCase):
    def test_empty_sentence_schema(self):
        result = MODULE.BrandVoiceAnalyzer()._analyze_sentences("")
        self.assertEqual(result, {"average_length": 0, "variety": "low", "count": 0})

    def test_whitespace_sentence_schema(self):
        for text in [" ", "\n\t\r", "\u2003\u00a0"]:
            with self.subTest(text=text):
                self.assertEqual(MODULE.BrandVoiceAnalyzer()._analyze_sentences(text)["count"], 0)

    def test_delimiter_only_sentence_schema(self):
        for text in [".", "?!...", " . \n ! ? "]:
            self.assertEqual(MODULE.BrandVoiceAnalyzer()._analyze_sentences(text)["count"], 0)

    def test_empty_text_report(self):
        output = MODULE.analyze_content("", "text")
        self.assertIn("Word Count: 0", output)
        self.assertIn("Total Sentences: 0", output)

    def test_json_has_zero_count(self):
        for text in ["", " \t\n", "?!"]:
            result = json.loads(MODULE.analyze_content(text, "json"))
            self.assertEqual(result["sentence_analysis"]["count"], 0)

    def test_nonempty_sentence_analysis(self):
        analyzer = MODULE.BrandVoiceAnalyzer()
        self.assertEqual(analyzer._analyze_sentences("Hi. Happy teams share ideas!"), {"average_length": 2.5, "variety": "low", "count": 2})
        self.assertEqual(analyzer._analyze_sentences("unfinished sentence")["count"], 1)

    def test_default_cli_handles_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.txt"
            path.write_text("")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("Total Sentences: 0", result.stdout)

    def test_cli_formats_handle_delimiter_only_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "punctuation.txt"
            path.write_text("?! . \n")
            for format_name in ["text", "json"]:
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path), "--format", format_name], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if format_name == "json":
                    self.assertEqual(json.loads(result.stdout)["sentence_analysis"]["count"], 0)
                else:
                    self.assertIn("Total Sentences: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()

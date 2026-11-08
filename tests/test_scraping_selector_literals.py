"""Validate generated selector literals without running generated scripts."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "engineering/browser-automation/scripts/scraping_toolkit.py"
SPEC = importlib.util.spec_from_file_location("scraping_generator", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
URL = "https://example.com/products"


def literal_fields(script):
    tree = ast.parse(script)
    node = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "FIELDS" for target in n.targets))
    return ast.literal_eval(node)


class ScrapingSelectorLiteralTests(unittest.TestCase):
    def assert_round_trip(self, selectors, paginate=False):
        script, error = MODULE.build_scraping_script(URL, selectors, paginate=paginate)
        self.assertIsNone(error)
        config, error = MODULE.build_scraping_script(URL, selectors, paginate=paginate, output_format="json")
        self.assertIsNone(error)
        fields = literal_fields(script)
        self.assertEqual(fields, config["selectors"])
        return fields

    def test_double_quoted_attribute(self):
        fields = self.assert_round_trip('input[type="text"]')
        self.assertEqual(list(fields.values()), ['input[type="text"]'])

    def test_single_and_mixed_quotes(self):
        for selector in ["[data-name='sample']", '[data-name="O\'Reilly"]']:
            with self.subTest(selector=selector):
                self.assertEqual(list(self.assert_round_trip(selector).values()), [selector])

    def test_css_backslashes_are_not_python_escapes(self):
        for selector in [r".group\32 span", r".item\:active", r'[data-label="line\nend"]']:
            with self.subTest(selector=selector):
                self.assertEqual(list(self.assert_round_trip(selector).values()), [selector])

    def test_unicode_and_selector_whitespace(self):
        for selector in ['[data-label="검색 🔎"]', "article\n.title"]:
            with self.subTest(selector=selector):
                self.assertEqual(list(self.assert_round_trip(selector).values()), [selector])

    def test_multiple_fields_and_pagination(self):
        selectors = '.title, input[type="text"], .price'
        for paginate in [False, True]:
            with self.subTest(paginate=paginate):
                fields = self.assert_round_trip(selectors, paginate)
                self.assertEqual(list(fields.values()), [".title", 'input[type="text"]', ".price"])

    def test_cli_script_and_json_modes(self):
        selector = 'input[type="text"]'
        for flags in [[], ["--paginate"], ["--json"]]:
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, "-B", str(SOURCE), "--url", URL,
                                         "--selectors", selector, *flags], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                fields = json.loads(result.stdout)["selectors"] if "--json" in flags else literal_fields(result.stdout)
                self.assertEqual(list(fields.values()), [selector])

    def test_empty_selector_error_is_preserved(self):
        self.assertEqual(MODULE.build_scraping_script(URL, " , "), (None, "No valid selectors provided."))
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "--url", URL, "--selectors", " , "],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("No valid selectors", result.stderr)

    def test_help(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--selectors", result.stdout)


if __name__ == "__main__":
    unittest.main()

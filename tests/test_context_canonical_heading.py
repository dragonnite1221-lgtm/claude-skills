"""Recognize canonical section titles as well as existing aliases."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/marketing-context/scripts/context_validator.py"
SPEC = importlib.util.spec_from_file_location("context_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
NAME = "Problems & Pain Points"


class ContextCanonicalHeadingTests(unittest.TestCase):
    def check_partial(self, text, markers=1):
        result = MODULE.validate_context(text)
        section = result["sections"][NAME]
        self.assertEqual(section["status"], "partial")
        self.assertEqual(section["markers_found"], markers)
        self.assertEqual(section["score"], round(10 * markers / 4))
        self.assertNotIn(NAME, result["missing_required"])
        return result

    def test_canonical_heading_with_cost(self):
        self.check_partial("## Problems & Pain Points\nCost: $100\n")

    def test_canonical_heading_with_tension(self):
        self.check_partial("## Problems & Pain Points\nEmotional tension: uncertainty\n")

    def test_canonical_heading_with_later_markers(self):
        self.check_partial("## Problems & Pain Points\nCost: $100\nTension: delays\n", 2)

    def test_heading_case_is_insensitive(self):
        self.check_partial("## PROBLEMS & PAIN POINTS\nCOST: $100\n")

    def test_existing_alias_and_marker_fallback(self):
        self.check_partial("## Problems Pain Points\nCost: $100\n")
        self.check_partial("Core problem: delays\n")

    def test_heading_still_requires_content_marker(self):
        result = MODULE.validate_context("## Problems & Pain Points\nNothing supplied yet.\n")
        self.assertEqual(result["sections"][NAME]["status"], "missing")
        self.assertIn(NAME, result["missing_required"])

    def test_cost_without_heading_remains_missing(self):
        result = MODULE.validate_context("Cost: $100\n")
        self.assertEqual(result["sections"][NAME]["status"], "missing")

    def test_cli_preserves_additive_json_contract(self):
        content = "## Problems & Pain Points\nCost: $100\n"
        expected = self.check_partial(content)
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            MODULE.print_report(expected)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "context.md"
            path.write_text(content)
            for json_mode in [False, True]:
                args = [sys.executable, "-B", str(SCRIPT), str(path)] + (["--json"] if json_mode else [])
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                suffix = "\n" + json.dumps(expected, indent=2) + "\n" if json_mode else ""
                self.assertEqual(result.stdout, text.getvalue() + suffix)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()

"""Verify that churn calculator JSON mode emits one JSON document."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/churn-prevention/scripts/churn_impact_calculator.py"
SPEC = importlib.util.spec_from_file_location("churn_calculator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ChurnJsonOutputTests(unittest.TestCase):
    def run_cli(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def expected_json(self, data):
        return json.dumps(MODULE.calculate(data), indent=2) + "\n"

    def test_demo_json_is_one_document(self):
        output = self.run_cli("--json")
        self.assertEqual(json.loads(output), MODULE.calculate(MODULE.SAMPLE_INPUT))
        self.assertEqual(output, self.expected_json(MODULE.SAMPLE_INPUT))

    def test_explicit_file_json_is_one_document(self):
        data = dict(MODULE.SAMPLE_INPUT, mrr=75000, voluntary_churn_pct=80)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(json.dumps(data))
            output = self.run_cli(str(path), "--json")
        self.assertEqual(json.loads(output), MODULE.calculate(data))
        self.assertEqual(output, self.expected_json(data))

    def test_json_flag_before_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input with spaces.json"
            path.write_text(json.dumps(MODULE.SAMPLE_INPUT))
            self.assertEqual(self.run_cli("--json", str(path)), self.expected_json(MODULE.SAMPLE_INPUT))

    def test_repeated_json_flag_still_one_document(self):
        self.assertEqual(self.run_cli("--json", "--json"), self.expected_json(MODULE.SAMPLE_INPUT))

    def test_default_human_demo_is_preserved(self):
        expected = io.StringIO()
        with contextlib.redirect_stdout(expected):
            print("No input file provided. Running with sample data...\n")
            print("Sample input:")
            print(json.dumps(MODULE.SAMPLE_INPUT, indent=2))
            MODULE.print_report(MODULE.calculate(MODULE.SAMPLE_INPUT))
        self.assertEqual(self.run_cli(), expected.getvalue())

    def test_explicit_human_report_is_preserved(self):
        expected = io.StringIO()
        with contextlib.redirect_stdout(expected):
            MODULE.print_report(MODULE.calculate(MODULE.SAMPLE_INPUT))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(json.dumps(MODULE.SAMPLE_INPUT))
            self.assertEqual(self.run_cli(str(path)), expected.getvalue())

    def test_help_keeps_json_contract(self):
        self.assertIn("Output results as JSON", self.run_cli("--help"))

    def test_calculate_preserves_input(self):
        data = copy.deepcopy(MODULE.SAMPLE_INPUT)
        MODULE.calculate(data)
        self.assertEqual(data, MODULE.SAMPLE_INPUT)


if __name__ == "__main__":
    unittest.main()

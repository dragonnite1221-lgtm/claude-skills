import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "business-growth/revenue-operations/scripts/forecast_accuracy_tracker.py"
SPEC = importlib.util.spec_from_file_location("forecast_empty_periods", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ForecastEmptyPeriodsTests(unittest.TestCase):
    def run_cli(self, data, output=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forecast data.json"
            raw = json.dumps(data).encode()
            path.write_bytes(raw)
            args = [sys.executable, str(SCRIPT), str(path)]
            if output is not None:
                args += ["--format", output]
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            self.assertEqual(path.read_bytes(), raw)
            return result

    def test_empty_analysis_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must contain at least one period"):
            MODULE.track_forecast_accuracy({"forecast_periods": []})

    def test_empty_with_categories_is_rejected_without_mutating(self):
        data = {"forecast_periods": [], "category_breakdowns": {
            "by_rep": [{"category": "A", "forecast": 100, "actual": 100}]}}
        before = copy.deepcopy(data)
        with self.assertRaises(ValueError):
            MODULE.track_forecast_accuracy(data)
        self.assertEqual(data, before)

    def test_empty_cli_is_clear_for_all_formats(self):
        for output in (None, "text", "json"):
            with self.subTest(output=output):
                result = self.run_cli({"forecast_periods": []}, output)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "Error: forecast_periods must contain at least one period\n")

    def test_missing_key_message_is_preserved(self):
        for output in ("text", "json"):
            with self.subTest(output=output):
                result = self.run_cli({}, output)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "Error: Missing required field 'forecast_periods' in input data\n")

    def test_exact_singleton_is_still_valid(self):
        data = {"forecast_periods": [{"period": "Q1", "forecast": 100, "actual": 100}]}
        result = MODULE.track_forecast_accuracy(data)
        self.assertEqual(result["periods_analyzed"], 1)
        self.assertEqual(result["mape"], 0)
        self.assertEqual(result["accuracy_rating"]["rating"], "Excellent")
        self.assertEqual(result["bias"]["avg_bias_amount"], 0)

    def test_nonempty_math_and_input_are_preserved(self):
        data = {"forecast_periods": [
            {"period": "Q1", "forecast": 80, "actual": 100},
            {"period": "Q2", "forecast": 220, "actual": 200}]}
        before = copy.deepcopy(data)
        result = MODULE.track_forecast_accuracy(data)
        self.assertEqual(result["mape"], 15)
        self.assertEqual(result["weighted_mape"], 13.3)
        self.assertEqual(result["bias"]["direction"], "Balanced")
        self.assertEqual(result["bias"]["avg_bias_amount"], 0)
        self.assertEqual(result["trend"]["trend"], "Improving")
        self.assertEqual(data, before)

    def test_nonempty_cli_json_stays_machine_readable(self):
        data = {"forecast_periods": [{"period": "Q1", "forecast": 80, "actual": 100}]}
        result = self.run_cli(data, "json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), MODULE.track_forecast_accuracy(data))

    def test_nonempty_cli_text_is_preserved(self):
        data = {"forecast_periods": [{"period": "Q1", "forecast": 80, "actual": 100}]}
        result = self.run_cli(data, "text")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, MODULE.format_text_report(MODULE.track_forecast_accuracy(data)) + "\n")


if __name__ == "__main__":
    unittest.main()

"""Preserve decimal magnitudes when extracting interview metrics."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "product-team/product-manager-toolkit/scripts/customer_interview_analyzer.py"
SPEC = importlib.util.spec_from_file_location("interview_metrics", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InterviewDecimalMetricsTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MODULE.InterviewAnalyzer()

    def test_decimal_percentages_preserve_whole_value(self):
        for value in ["12.5", "0.25", "100.00"]:
            with self.subTest(value=value):
                self.assertEqual(self.analyzer._extract_metrics(f"Conversion is {value}%."), [f"{value}%"])

    def test_decimal_time_units_preserve_whole_value(self):
        for unit in ["hour", "hours", "minute", "minutes", "day", "days", "week", "weeks", "month", "months"]:
            with self.subTest(unit=unit):
                self.assertEqual(self.analyzer._extract_metrics(f"We save 1.5 {unit}."), [f"1.5 {unit}"])
        self.assertEqual(self.analyzer._extract_metrics("It takes 2.25HOURS."), ["2.25HOURS"])

    def test_decimal_currency_preserves_cents(self):
        for value in ["12.50", "0.99", "1,250.75"]:
            with self.subTest(value=value):
                self.assertEqual(self.analyzer._extract_metrics(f"Cost: ${value}."), [f"${value}"])

    def test_decimal_numbers_with_context(self):
        for value in ["2.75", "0.5", "10.00"]:
            with self.subTest(value=value):
                self.assertEqual(self.analyzer._extract_metrics(f"We average {value} tasks."), [f"{value} tasks"])

    def test_integer_controls_and_stop_words(self):
        actual = set(self.analyzer._extract_metrics("10% and 2 hours cost $50 for 3 users."))
        self.assertEqual(actual, {"10%", "2 hours", "$50", "50 for", "3 users"})
        self.assertEqual(self.analyzer._extract_metrics("2 the 3 and 4 of"), [])

    def test_repeated_metric_is_deduplicated(self):
        self.assertEqual(self.analyzer._extract_metrics("Save 1.5 hours, then save 1.5 hours."), ["1.5 hours"])

    def test_json_and_text_cli_preserve_transcript(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "interview.txt"
            path.write_text("Conversion is 12.5%. We save 1.5 hours. Cost: $12.50. Average: 2.75 tasks.")
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            expected = {"12.5%", "1.5 hours", "$12.50", "2.75 tasks"}
            for flags in [["--json"], []]:
                with self.subTest(flags=flags):
                    result = subprocess.run([sys.executable, "-B", str(SOURCE), str(path), *flags],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    if flags:
                        self.assertEqual(set(json.loads(result.stdout)["metrics_mentioned"]), expected)
                    else:
                        for metric in expected:
                            self.assertIn(metric, result.stdout)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_help(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--json", result.stdout)


if __name__ == "__main__":
    unittest.main()

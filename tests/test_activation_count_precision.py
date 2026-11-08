"""Regression tests for count-based onboarding improvement estimates."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/onboarding-cro/scripts/activation_funnel_analyzer.py"
SPEC = importlib.util.spec_from_file_location("activation_funnel", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def funnel(counts):
    return {"steps": [{"name": f"Step {i}", "users": n} for i, n in enumerate(counts)]}


class ActivationCountPrecisionTests(unittest.TestCase):
    def improvement(self, counts):
        return MODULE.analyze_funnel(funnel(counts))["improvements"][0]

    def test_small_drop_does_not_disappear(self):
        result = self.improvement([100000, 99960])
        self.assertEqual(result["users_saved"], 20)
        self.assertEqual(result["additional_activated"], 20)
        self.assertEqual(result["current_drop"], "0.0%")

    def test_rounded_rates_do_not_bias_counts(self):
        for end, expected in [(876540, 61730), (876400, 61800), (666666, 166667)]:
            with self.subTest(end=end):
                result = self.improvement([1000000, end])
                self.assertEqual(result["users_saved"], expected)
                self.assertEqual(result["additional_activated"], expected)

    def test_odd_drops_keep_integer_truncation(self):
        for lost in [1, 3, 39, 41, 333333]:
            with self.subTest(lost=lost):
                result = self.improvement([1000000, 1000000 - lost])
                self.assertEqual(result["users_saved"], lost // 2)
                self.assertIsInstance(result["users_saved"], int)

    def test_corrected_counts_propagate_downstream(self):
        result = self.improvement([1000000, 876540, 800000])
        self.assertEqual(result["users_saved"], 61730)
        self.assertEqual(result["additional_activated"], 56339)
        self.assertEqual(result["impact_on_overall"], "+5.6pp")

    def test_sample_summary_and_input_are_preserved(self):
        data = copy.deepcopy(MODULE.SAMPLE_DATA)
        before = copy.deepcopy(data)
        result = MODULE.analyze_funnel(data)
        self.assertEqual(result["summary"]["total_activated"], 72)
        self.assertEqual(result["summary"]["worst_step"], "First project created")
        self.assertEqual(result["improvements"][0]["users_saved"], 145)
        self.assertEqual(result["improvements"][0]["additional_activated"], 36)
        self.assertEqual(data, before)

    def test_zero_and_no_drop_funnels(self):
        for counts in [[0, 0], [1000, 1000]]:
            self.assertEqual(MODULE.analyze_funnel(funnel(counts))["improvements"], [])

    def test_json_cli_reports_exact_saved_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funnel.json"
            path.write_text(json.dumps(funnel([100000, 99960])))
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path), "--json"], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["improvements"][0]["users_saved"], 20)

    def test_human_cli_reports_corrected_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funnel.json"
            path.write_text(json.dumps(funnel([1000000, 876400])))
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Users saved at step: +61800", process.stdout)
        self.assertIn("Additional activated: +61800", process.stdout)


if __name__ == "__main__":
    unittest.main()

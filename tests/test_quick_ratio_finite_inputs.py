import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "finance/saas-metrics-coach/scripts/quick_ratio_calculator.py"
FIELDS = ("--new-mrr", "--expansion", "--churned", "--contraction")


def reject_constant(value):
    raise ValueError("Nonstandard JSON constant: " + value)


class FiniteInputTests(unittest.TestCase):
    def cli(self, values=None, output_json=True):
        data = dict(zip(FIELDS, ("10000", "2000", "3000", "500")))
        data.update(values or {})
        args = [key + "=" + value for key, value in data.items()]
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args, *(["--json"] if output_json else [])], capture_output=True, text=True)

    def rejected(self, result):
        self.assertEqual((result.returncode, result.stdout), (2, ""))
        self.assertIn("MRR inputs must be finite numbers", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_nan_rejected_for_every_component(self):
        for field in FIELDS:
            with self.subTest(field=field):
                self.rejected(self.cli({field: "nan"}))

    def test_infinities_rejected_for_every_component(self):
        for field in FIELDS:
            for value in ("inf", "+inf", "-inf", "Infinity"):
                with self.subTest(field=field, value=value):
                    self.rejected(self.cli({field: value}))

    def test_overflow_literals_rejected(self):
        for field in FIELDS:
            with self.subTest(field=field):
                self.rejected(self.cli({field: "1e309"}))

    def test_human_mode_also_rejects_nonfinite(self):
        self.rejected(self.cli({"--new-mrr": "nan"}, output_json=False))
        self.rejected(self.cli({"--churned": "-Infinity"}, output_json=False))

    def test_finite_examples_keep_calculation(self):
        result = self.cli()
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        data = json.loads(result.stdout, parse_constant=reject_constant)
        self.assertAlmostEqual(data["quick_ratio"], 24 / 7)
        self.assertEqual(data["quick_ratio_display"], "3.43")
        self.assertEqual(data["status"], "HEALTHY")
        result = self.cli({"--new-mrr": "200", "--expansion": "0", "--churned": "100", "--contraction": "0"})
        self.assertEqual(json.loads(result.stdout, parse_constant=reject_constant)["quick_ratio"], 2.0)

    def test_zero_loss_keeps_null_or_zero_ratio(self):
        result = self.cli({"--churned": "0", "--contraction": "0"})
        data = json.loads(result.stdout, parse_constant=reject_constant)
        self.assertIsNone(data["quick_ratio"])
        self.assertEqual(data["quick_ratio_display"], "∞")
        self.assertEqual(data["status"], "EXCELLENT")
        data = json.loads(self.cli(dict.fromkeys(FIELDS, "0")).stdout, parse_constant=reject_constant)
        self.assertEqual(data["quick_ratio"], 0)

    def test_help_still_works(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertIn("--new-mrr", result.stdout)

    def test_direct_api_for_finite_values_unchanged(self):
        spec = importlib.util.spec_from_file_location("quick_ratio_finite_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.calculate_quick_ratio(200, 0, 100, 0)["quick_ratio"], 2.0)
        self.assertIsNone(module.calculate_quick_ratio(100, 0, 0, 0)["quick_ratio"])


if __name__ == "__main__":
    unittest.main()

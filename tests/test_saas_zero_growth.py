"""A measured zero must not be confused with a missing growth input."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "finance/saas-metrics-coach/scripts/metrics_calculator.py"
SPEC = importlib.util.spec_from_file_location("saas_metrics", SCRIPT)
METRICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(METRICS)
MISSING_GROWTH = "MoM Growth — need last month MRR"


class ZeroGrowthTests(unittest.TestCase):
    def cli(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        return result.stdout

    def test_zero_current_mrr_is_complete_revenue_loss(self):
        for current in (0, 0.0, -0.0):
            result = METRICS.calculate(mrr=current, mrr_last=1000)
            self.assertEqual(result["MoM_Growth_Pct"], -100)
            self.assertNotIn(MISSING_GROWTH, result["_missing"])
            self.assertEqual((result["MRR"], result["ARR"]), (0, 0))

    def test_flat_growth_keeps_rule_of_40(self):
        for profit in (0, 10, -10, 40):
            result = METRICS.calculate(mrr=1000, mrr_last=1000, profit_margin=profit)
            self.assertEqual(result["MoM_Growth_Pct"], 0)
            self.assertEqual(result["Rule_of_40"], profit)

    def test_rounded_zero_growth_keeps_existing_formula(self):
        for current in (999999, 1000001):
            result = METRICS.calculate(mrr=current, mrr_last=1000000, profit_margin=15)
            self.assertEqual(result["MoM_Growth_Pct"], 0)
            self.assertEqual(result["Rule_of_40"], 15)

    def test_missing_or_nonpositive_previous_mrr_stays_missing(self):
        for previous in (None, 0, -1):
            result = METRICS.calculate(mrr=0, mrr_last=previous, profit_margin=10)
            self.assertNotIn("MoM_Growth_Pct", result)
            self.assertNotIn("Rule_of_40", result)
            self.assertIn(MISSING_GROWTH, result["_missing"])

    def test_missing_current_or_profit_is_not_assumed_zero(self):
        result = METRICS.calculate(mrr=None, mrr_last=1000, profit_margin=10)
        self.assertNotIn("MoM_Growth_Pct", result)
        self.assertNotIn("Rule_of_40", result)
        result = METRICS.calculate(mrr=1000, mrr_last=1000)
        self.assertNotIn("Rule_of_40", result)

    def test_nonzero_growth_formula_is_preserved(self):
        for current, expected in ((500, -50), (1500, 50)):
            result = METRICS.calculate(mrr=current, mrr_last=1000, profit_margin=10)
            self.assertEqual(result["MoM_Growth_Pct"], expected)
            self.assertEqual(result["Rule_of_40"], expected * 12 + 10)

    def test_json_cli_zero_and_flat_revenue(self):
        for current in (0, 1000):
            actual = json.loads(self.cli("--mrr", str(current), "--mrr-last", "1000",
                                         "--profit-margin", "10", "--json"))
            self.assertEqual(actual, METRICS.calculate(mrr=current, mrr_last=1000,
                                                       profit_margin=10))

    def test_human_cli_flat_growth_includes_rule_of_40(self):
        text = self.cli("--mrr", "1000", "--mrr-last", "1000", "--profit-margin", "0")
        self.assertIn("MoM MRR Growth", text)
        self.assertIn("Rule of 40 Score", text)
        self.assertIn("0.0%", text)


if __name__ == "__main__":
    unittest.main()

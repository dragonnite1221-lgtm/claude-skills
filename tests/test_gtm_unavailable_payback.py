"""CAC payback requires a positive monthly contribution."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "business-growth/revenue-operations/scripts/gtm_efficiency_calculator.py"
SPEC = importlib.util.spec_from_file_location("gtm_payback", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DATA = {
    "revenue": {"net_new_arr": 1200000, "arpa_monthly": 2500, "revenue_growth_pct": 31.6},
    "costs": {"sales_marketing_spend": 1800000, "cac": 18000,
              "gross_margin_pct": 78, "net_burn": 1500000, "fcf_margin_pct": 8.4},
    "customers": {"beginning_arr": 3800000, "expansion_arr": 600000,
                  "contraction_arr": 100000, "churned_arr": 300000,
                  "annual_churn_rate_pct": 8},
}


class PaybackTests(unittest.TestCase):
    def test_zero_arpa_is_unavailable(self):
        result = MODULE.calculate_cac_payback(18000, 0, 78)
        self.assertIsNone(result["months"])
        self.assertEqual(result["rating"], "N/A")
        self.assertEqual(result["percentile"], "N/A")

    def test_zero_margin_is_unavailable(self):
        result = MODULE.calculate_cac_payback(18000, 2500, 0)
        self.assertIsNone(result["months"])
        self.assertIn("Positive monthly contribution", result["label"])

    def test_negative_contribution_is_unavailable(self):
        for arpa, margin in [(2500, -10), (-100, 78)]:
            with self.subTest(arpa=arpa, margin=margin):
                result = MODULE.calculate_cac_payback(18000, arpa, margin)
                self.assertIsNone(result["months"])
                self.assertNotEqual(result["rating"], "Green")

    def test_zero_cost_without_contribution_is_undefined(self):
        self.assertIsNone(MODULE.calculate_cac_payback(0, 0, 78)["months"])

    def test_positive_contribution_preserves_formula_and_rating(self):
        result = MODULE.calculate_cac_payback(18000, 2500, 78)
        self.assertEqual(result["months"], round(18000 / 1950, 1))
        self.assertEqual(result["rating"], "Green")
        self.assertEqual(result["percentile"], "Top 10%")

    def test_zero_cost_with_positive_contribution_is_zero(self):
        self.assertEqual(MODULE.calculate_cac_payback(0, 2500, 78)["months"], 0)

    def test_slow_payback_still_recommends_improvement(self):
        data = copy.deepcopy(DATA)
        data["costs"]["cac"] = 60000
        result = MODULE.calculate_all_metrics(data)
        self.assertEqual(result["cac_payback"]["rating"], "Red")
        self.assertTrue(any("Capital recovery is too slow" in r
                            for r in result["recommendations"]))

    def test_unavailable_report_and_recommendation(self):
        data = copy.deepcopy(DATA)
        data["costs"]["gross_margin_pct"] = 0
        original = copy.deepcopy(data)
        result = MODULE.calculate_all_metrics(data)
        self.assertEqual(data, original)
        self.assertIn('"months": null', json.dumps(result, allow_nan=False))
        text = MODULE.format_text_report(result)
        self.assertIn("CAC PAYBACK: N/A", text)
        self.assertNotIn("None months", text)
        self.assertNotIn("Healthy payback", text)
        self.assertTrue(any("without positive monthly contribution" in r
                            for r in result["recommendations"]))

    def test_cli_json_and_text(self):
        data = copy.deepcopy(DATA)
        data["revenue"]["arpa_monthly"] = 0
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text(json.dumps(data))
            for format_name in ("json", "text"):
                with self.subTest(format=format_name):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), str(path), "--format", format_name],
                        text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    if format_name == "json":
                        self.assertIsNone(json.loads(result.stdout)["cac_payback"]["months"])
                    else:
                        self.assertIn("CAC PAYBACK: N/A", result.stdout)
                        self.assertNotIn("Healthy payback", result.stdout)


if __name__ == "__main__":
    unittest.main()

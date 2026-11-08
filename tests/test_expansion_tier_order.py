"""Tier upgrade estimates must choose the next tier regardless of input order."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "business-growth/customer-success-manager/scripts/expansion_opportunity_scorer.py"
SPEC = importlib.util.spec_from_file_location("expansion_order", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
TIERS = ["starter", "professional", "enterprise", "enterprise_plus"]
CUSTOMER = {
    "customer_id": "synthetic-tier", "name": "Synthetic Tier",
    "segment": "smb", "arr": 10000,
    "contract": {"licensed_seats": 10, "active_seats": 1, "plan_tier": "starter",
                 "available_tiers": ["enterprise_plus", "enterprise", "professional"]},
    "product_usage": {}, "departments": {"current": [], "potential": []},
}


class TierOrderTests(unittest.TestCase):
    def test_all_starter_upgrade_orders(self):
        for tiers in itertools.permutations(TIERS[1:]):
            with self.subTest(tiers=tiers):
                revenue, target, rationale = MODULE.estimate_tier_upgrade_revenue(
                    10000, "starter", list(tiers))
                self.assertEqual((revenue, target), (8000, "professional"))
                self.assertIn("$8,000 ARR", rationale)

    def test_each_current_tier_across_all_orders(self):
        for tiers in itertools.permutations(TIERS):
            for current, arr, revenue, target in [
                ("starter", 10000, 8000, "professional"),
                ("professional", 18000, 12000, "enterprise"),
                ("enterprise", 30000, 15000, "enterprise_plus"),
                ("enterprise_plus", 45000, 0, None),
            ]:
                with self.subTest(tiers=tiers, current=current):
                    result = MODULE.estimate_tier_upgrade_revenue(arr, current, list(tiers))
                    self.assertEqual(result[:2], (revenue, target))

    def test_only_available_higher_tier_is_selected(self):
        result = MODULE.estimate_tier_upgrade_revenue(
            10000, "starter", ["enterprise_plus", "enterprise"])
        self.assertEqual(result[:2], (20000, "enterprise"))

    def test_case_insensitive_matching_preserves_target_spelling(self):
        result = MODULE.estimate_tier_upgrade_revenue(
            18000, "PROFESSIONAL", ["ENTERPRISE_PLUS", "Enterprise"])
        self.assertEqual(result[:2], (12000, "Enterprise"))

    def test_no_higher_tier_keeps_no_upgrade(self):
        for tiers in [[], ["starter", "professional"], ["unrecognized"]]:
            result = MODULE.estimate_tier_upgrade_revenue(30000, "enterprise", tiers)
            self.assertEqual(result, (0.0, None, "Already on highest tier"))

    def test_zero_or_negative_arr_has_no_positive_opportunity(self):
        for arr in [0, -100]:
            result = MODULE.estimate_tier_upgrade_revenue(arr, "starter", TIERS)
            self.assertEqual(result[:2], (0.0, None))

    def test_analysis_preserves_input_and_corrects_total(self):
        customer = copy.deepcopy(CUSTOMER)
        original = copy.deepcopy(customer)
        result = MODULE.analyse_expansion(customer)
        self.assertEqual(customer, original)
        self.assertEqual(result["opportunity_count"], 1)
        self.assertEqual(result["total_estimated_revenue"], 8000)
        self.assertEqual(result["opportunities"][0]["target_tier"], "professional")
        self.assertEqual(result["opportunities"][0]["priority_score"], 8)

    def test_report_summary_uses_correct_upgrade_revenue(self):
        result = MODULE.analyse_expansion(CUSTOMER)
        output = json.loads(MODULE.format_json([result]))
        self.assertEqual(output["summary"]["total_estimated_revenue"], 8000)
        self.assertIn("Total Expansion Revenue Potential: $8,000", MODULE.format_text([result]))

    def test_cli_json_and_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text(json.dumps({"customers": [CUSTOMER]}))
            for format_name in ("json", "text"):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", format_name],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if format_name == "json":
                    output = json.loads(result.stdout)
                    self.assertEqual(output["summary"]["total_estimated_revenue"], 8000)
                else:
                    self.assertIn("Upgrade from starter to professional", result.stdout)
                    self.assertIn("Total Expansion Revenue Potential: $8,000", result.stdout)


if __name__ == "__main__":
    unittest.main()

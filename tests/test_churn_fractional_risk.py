"""Fractional churn scores must not fall into lower-risk gaps."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "business-growth/customer-success-manager/scripts/churn_risk_analyzer.py"
SPEC = importlib.util.spec_from_file_location("churn_fractional", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def customer(high=False):
    record = {
        "customer_id": "synthetic-gap", "name": "Synthetic Gap",
        "segment": "mid-market", "arr": 120000, "contract_end_date": None,
        "usage_decline": {"login_trend": -34, "feature_adoption_change": -25,
                          "dau_mau_change": -0.2},
        "engagement_drop": {"meeting_cancellations": 4,
                            "response_time_days": 7.1, "nps_change": -5},
        "support_issues": {"open_escalations": 0, "unresolved_critical": 0,
                           "satisfaction_trend": "stable"},
        "relationship_signals": {"champion_left": False, "sponsor_change": False,
                                  "competitor_mentions": 0},
        "commercial_factors": {"contract_type": "annual",
                               "pricing_complaints": True, "budget_cuts_mentioned": False},
    }
    if high:
        record["support_issues"].update(open_escalations=3, unresolved_critical=2)
        record["relationship_signals"]["sponsor_change"] = True
        record["commercial_factors"]["contract_type"] = "quarterly"
    return record


class FractionalRiskTests(unittest.TestCase):
    def test_every_tenth_covers_contiguous_tiers(self):
        for tenth in range(1001):
            score = tenth / 10
            expected = ("critical" if score >= 80 else "high" if score >= 60
                        else "medium" if score >= 40 else "low")
            with self.subTest(score=score):
                self.assertEqual(MODULE.get_risk_tier(score)["name"], expected)

    def test_subtenth_threshold_edges(self):
        for score, expected in [(39.999, "low"), (40, "medium"),
                                (59.999, "medium"), (60, "high"),
                                (79.999, "high"), (80, "critical")]:
            self.assertEqual(MODULE.get_risk_tier(score)["name"], expected)

    def test_out_of_domain_fallback_is_preserved(self):
        for score in [-1, 100.1, float("inf"), float("-inf"), float("nan")]:
            self.assertEqual(MODULE.get_risk_tier(score)["name"], "low")

    def test_medium_fractional_pipeline_and_input_preservation(self):
        data = customer()
        original = copy.deepcopy(data)
        result = MODULE.analyse_churn_risk(data)
        self.assertEqual(data, original)
        self.assertEqual(result["risk_score"], 59.5)
        self.assertEqual(result["risk_tier"], "medium")
        self.assertIn("Schedule proactive check-in within 2 weeks",
                      result["recommended_actions"])

    def test_high_fractional_pipeline_and_playbook(self):
        result = MODULE.analyse_churn_risk(customer(True))
        self.assertEqual(result["risk_score"], 79.5)
        self.assertEqual(result["risk_label"], "HIGH")
        self.assertIn("Schedule urgent CSM call within 1 week",
                      result["recommended_actions"])

    def test_json_summary_counts_arr_at_risk(self):
        results = [MODULE.analyse_churn_risk(customer(v)) for v in [False, True]]
        summary = json.loads(MODULE.format_json(results))["summary"]
        self.assertEqual(summary["medium_count"], 1)
        self.assertEqual(summary["high_count"], 1)
        self.assertEqual(summary["low_count"], 0)
        self.assertEqual(summary["total_arr_at_risk"], 120000)

    def test_text_labels_and_arr(self):
        results = [MODULE.analyse_churn_risk(customer(v)) for v in [False, True]]
        text = MODULE.format_text(results)
        self.assertIn("59.5/100  [MEDIUM]", text)
        self.assertIn("79.5/100  [HIGH]", text)
        self.assertIn("ARR at Risk (Critical + High): $120,000", text)

    def test_cli_json_and_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text(json.dumps({"customers": [customer(), customer(True)]}))
            for format_name in ("json", "text"):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", format_name],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if format_name == "json":
                    summary = json.loads(result.stdout)["summary"]
                    self.assertEqual(summary["total_arr_at_risk"], 120000)
                    self.assertEqual(summary["low_count"], 0)
                else:
                    self.assertIn("59.5/100  [MEDIUM]", result.stdout)
                    self.assertIn("79.5/100  [HIGH]", result.stdout)


if __name__ == "__main__":
    unittest.main()

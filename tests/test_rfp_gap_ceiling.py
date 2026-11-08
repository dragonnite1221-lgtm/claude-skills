"""The must-have gap ceiling applies to both bid paths."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "business-growth/sales-engineer/scripts/rfp_response_analyzer.py"
SPEC = importlib.util.spec_from_file_location("rfp_gap_ceiling", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DATA = {
    "rfp_name": "Synthetic gap ceiling", "strategic_value": "high",
    "requirements": [
        {"id": str(i), "requirement": "Synthetic capability " + str(i),
         "category": "Core", "priority": "must-have",
         "coverage_status": "full" if i < 16 else "gap"}
        for i in range(20)
    ],
}


class GapCeilingTests(unittest.TestCase):
    def test_above_ceiling_never_bids(self):
        for coverage in [0, 39.9, 40, 49.9, 50, 69.9, 70, 80, 100]:
            for gaps in [4, 8]:
                for value in ["low", "medium", "high"]:
                    with self.subTest(coverage=coverage, gaps=gaps, value=value):
                        result = MODULE.determine_bid_recommendation(coverage, gaps, value)
                        self.assertEqual(result["decision"], "NO-BID")
                        self.assertIn(
                            str(gaps) + " must-have gaps exceed maximum of 3",
                            result["reasons"],
                        )

    def test_ceiling_boundary_keeps_existing_coverage_behavior(self):
        for coverage, expected in [(39.9, "NO-BID"), (40, "CONDITIONAL BID"),
                                   (50, "CONDITIONAL BID"), (69.9, "CONDITIONAL BID"),
                                   (70, "BID"), (100, "BID")]:
            self.assertEqual(
                MODULE.determine_bid_recommendation(coverage, 3, "medium")["decision"],
                expected,
            )

    def test_low_strategic_value_keeps_conditional_rejection(self):
        result = MODULE.determine_bid_recommendation(60, 2, "low")
        self.assertEqual(result["decision"], "NO-BID")
        self.assertIn("Low strategic value", result["reasons"][-1])

    def test_high_value_cannot_override_gap_ceiling(self):
        result = MODULE.determine_bid_recommendation(80, 4, "HIGH")
        self.assertEqual(result["decision"], "NO-BID")
        self.assertFalse(any("supports pursuing" in r for r in result["reasons"]))
        self.assertFalse(any("conditional range" in r for r in result["reasons"]))

    def test_full_analysis_preserves_input_and_scores(self):
        data = copy.deepcopy(DATA)
        original = copy.deepcopy(data)
        result = MODULE.analyze_rfp(data)
        self.assertEqual(data, original)
        self.assertEqual(result["coverage_summary"]["overall_coverage_percentage"], 80)
        self.assertEqual(result["coverage_summary"]["must_have_gaps"], 4)
        self.assertEqual(result["bid_recommendation"]["decision"], "NO-BID")
        self.assertEqual(len(result["gap_analysis"]), 4)
        self.assertEqual(result["category_scores"]["Core"]["coverage_percentage"], 80)

    def test_text_report_uses_no_bid_and_reason(self):
        text = MODULE.format_text(MODULE.analyze_rfp(DATA))
        self.assertIn("BID RECOMMENDATION: NO-BID", text)
        self.assertIn("4 must-have gaps exceed maximum of 3", text)

    def test_cli_json_and_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text(json.dumps(DATA))
            for format_name in ("json", "text"):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", format_name],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if format_name == "json":
                    output = json.loads(result.stdout)
                    self.assertEqual(output["bid_recommendation"]["decision"], "NO-BID")
                else:
                    self.assertIn("BID RECOMMENDATION: NO-BID", result.stdout)


if __name__ == "__main__":
    unittest.main()

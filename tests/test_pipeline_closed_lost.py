import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "business-growth/revenue-operations/scripts/pipeline_analyzer.py"
SPEC = importlib.util.spec_from_file_location("pipeline_closed_lost", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
STAGES = ["Discovery", "Proposal", "Closed Won", "Closed Lost"]


def fixture():
    def deal(name, stage, value, age):
        return {"id": name, "name": name, "stage": stage, "value": value,
                "age_days": age, "close_date": "2027-01-15"}
    return {"quota": 1000, "average_cycle_days": 45, "stages": STAGES.copy(),
            "deals": [deal("open", "Discovery", 100, 5),
                      deal("won", "Closed Won", 50, 20),
                      deal("lost", "Closed Lost", 4000, 999)]}


class ClosedLostTests(unittest.TestCase):
    def test_coverage_excludes_both_terminal_outcomes(self):
        result = MODULE.calculate_coverage_ratio(fixture()["deals"], 1000)
        self.assertEqual(result["total_pipeline_value"], 100)
        self.assertEqual(result["coverage_ratio"], 0.1)
        self.assertEqual(result["rating"], "Critical")

    def test_aging_ignores_lost_records_and_stage(self):
        data = fixture()
        result = MODULE.analyze_deal_aging(data["deals"], 45, STAGES)
        self.assertEqual(result["total_open_deals"], 1)
        self.assertEqual(result["healthy_deals"], 1)
        self.assertEqual(result["aging_deals"], [])
        self.assertEqual(result["stage_thresholds"], {"Discovery": 90, "Proposal": 67})

    def test_risk_matches_open_pipeline_without_lost(self):
        data = fixture()
        result = MODULE.assess_pipeline_risk(data["deals"], 1000, STAGES)
        expected = MODULE.assess_pipeline_risk(data["deals"][:2], 1000, STAGES[:-1])
        self.assertEqual(result, expected)
        self.assertNotIn("Closed Lost", result["stage_distribution"])
        self.assertEqual(result["coverage_gaps"][0]["pipeline_value"], 100)

    def test_loss_does_not_establish_successful_progression(self):
        conversions = MODULE.calculate_stage_conversion_rates(fixture()["deals"], STAGES)
        self.assertEqual(len(conversions), 2)
        self.assertEqual(conversions[0], {"from_stage": "Discovery", "to_stage": "Proposal",
                         "from_count": 2, "to_count": 1, "conversion_rate_pct": 50.0})
        self.assertEqual(conversions[1]["to_stage"], "Closed Won")
        self.assertEqual(conversions[1]["to_count"], 1)

    def test_lost_stage_position_does_not_change_open_analysis(self):
        data = fixture()
        expected = MODULE.analyze_pipeline(data)
        for index in range(4):
            with self.subTest(index=index):
                stages = STAGES[:-1].copy()
                stages.insert(index, "Closed Lost")
                candidate = dict(data, stages=stages)
                self.assertEqual(MODULE.analyze_pipeline(candidate), expected)

    def test_sales_velocity_retains_loss_history(self):
        result = MODULE.calculate_sales_velocity(fixture()["deals"])
        self.assertEqual(result["num_opportunities"], 3)
        self.assertEqual(result["win_rate_pct"], 33.3)
        self.assertEqual(result["avg_deal_size"], 1383.33)

    def test_all_lost_has_no_open_pipeline_or_successes(self):
        data = fixture()
        data["deals"] = data["deals"][2:]
        result = MODULE.analyze_pipeline(data)
        self.assertEqual(result["coverage"]["total_pipeline_value"], 0)
        self.assertEqual(result["aging"]["total_open_deals"], 0)
        self.assertTrue(all(c["to_count"] == 0 for c in result["stage_conversions"]))

    def test_inputs_are_preserved(self):
        data = fixture()
        original = copy.deepcopy(data)
        MODULE.analyze_pipeline(data)
        self.assertEqual(data, original)

    def test_cli_formats_use_corrected_pipeline(self):
        data = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pipeline data.json"
            raw = json.dumps(data).encode()
            path.write_bytes(raw)
            for output in ("json", "text"):
                with self.subTest(output=output):
                    result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(path),
                                             "--format", output], capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(result.stderr, "")
                    if output == "json":
                        self.assertEqual(json.loads(result.stdout), MODULE.analyze_pipeline(data))
                    else:
                        self.assertIn("Total Pipeline:   $100", result.stdout)
                        self.assertNotIn("Closed Lost", result.stdout)
                    self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()

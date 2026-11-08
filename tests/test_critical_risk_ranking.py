"""The three specific critical-risk recommendations must use weighted score order."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / (
    "project-management/senior-pm/scripts/risk_matrix_analyzer.py"
)
spec = importlib.util.spec_from_file_location("risk_matrix_analyzer", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

RECORDS = [
    {"title": "Business", "category": "business", "probability": 4, "impact": 4},
    {"title": "Financial", "category": "financial", "probability": 4, "impact": 4},
    {"title": "Technical", "category": "technical", "probability": 4, "impact": 5},
    {"title": "Highest", "category": "regulatory", "probability": 5, "impact": 5},
]


def titles(recommendations):
    return [line.split(" - ", 1)[1].split(": Implement", 1)[0]
            for line in recommendations if line.startswith("Critical Risk - ")]


def recommend(records):
    return tool.generate_risk_recommendations([tool.Risk(r) for r in records], {})


class CriticalRiskRankingTests(unittest.TestCase):
    def test_highest_late_risk_is_not_omitted(self):
        self.assertEqual(titles(recommend(RECORDS)), ["Highest", "Technical", "Financial"])
        self.assertIn("Address 4 critical risks", recommend(RECORDS)[0])

    def test_all_input_permutations_keep_top_three(self):
        for records in itertools.permutations(RECORDS):
            with self.subTest(order=[r["title"] for r in records]):
                self.assertEqual(titles(recommend(records)),
                                 ["Highest", "Technical", "Financial"])

    def test_closed_and_noncritical_risks_are_excluded(self):
        records = [
            dict(RECORDS[-1], title="Closed", status="closed"),
            {"title": "Low", "probability": 1, "impact": 1},
        ] + RECORDS[:3]
        self.assertEqual(titles(recommend(records)), ["Technical", "Financial", "Business"])

    def test_equal_scores_preserve_input_order(self):
        records = [dict(RECORDS[-1], title=label) for label in ["B", "D", "A", "C"]]
        self.assertEqual(titles(recommend(records)), ["B", "D", "A"])

    def test_small_and_empty_critical_sets(self):
        self.assertEqual(titles(recommend([])), [])
        self.assertEqual(titles(recommend(RECORDS[:1])), ["Business"])
        self.assertEqual(titles(recommend(RECORDS[:2])), ["Financial", "Business"])
        self.assertEqual(titles(recommend(RECORDS[:3])), ["Technical", "Financial", "Business"])

    def test_analysis_keeps_inputs_scores_and_total_count(self):
        data = {"risks": copy.deepcopy(RECORDS)}
        saved = copy.deepcopy(data)
        result = tool.analyze_risks(data)
        self.assertEqual(data, saved)
        self.assertEqual(result.summary["critical_risks"], 4)
        self.assertAlmostEqual(result.summary["total_risk_exposure"], 104.7)
        self.assertEqual(result.risk_matrix["distribution"]["critical"], 4)
        self.assertEqual(titles(result.recommendations), ["Highest", "Technical", "Financial"])

    def test_json_and_text_cli_prioritize_same_risks(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "risks.json"
            path.write_text(json.dumps({"risks": RECORDS}))
            for fmt in ["json", "text"]:
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", fmt],
                    capture_output=True, text=True, check=True)
                self.assertEqual(result.stderr, "")
                if fmt == "json":
                    recs = json.loads(result.stdout)["recommendations"]
                    self.assertEqual(titles(recs), ["Highest", "Technical", "Financial"])
                else:
                    a = result.stdout.index("Critical Risk - Highest:")
                    b = result.stdout.index("Critical Risk - Technical:")
                    c = result.stdout.index("Critical Risk - Financial:")
                    self.assertLess(a, b)
                    self.assertLess(b, c)
                    self.assertNotIn("Critical Risk - Business:", result.stdout)


if __name__ == "__main__":
    unittest.main()

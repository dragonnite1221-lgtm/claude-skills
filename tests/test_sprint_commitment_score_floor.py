"""Keep commitment and aggregate health scores in their advertised 0-100 range."""
import copy
import importlib.util
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / (
    "project-management/scrum-master/scripts/sprint_health_scorer.py"
)
spec = importlib.util.spec_from_file_location("sprint_health_scorer", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def score(ratios):
    return tool.score_commitment_reliability([
        tool.SprintHealthData({"planned_points": 1, "completed_points": value})
        for value in ratios
    ])


class CommitmentFloorTests(unittest.TestCase):
    def test_extreme_inconsistency_has_zero_floor(self):
        result = score([20, 0])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["grade"], "poor")
        self.assertEqual(result["average_commitment"], 10)
        self.assertEqual(result["commitment_ratios"], [20, 0])
        self.assertLess(result["consistency"], 0)

    def test_full_health_score_is_bounded(self):
        data = {"sprints": [
            {"sprint_number": 1, "planned_points": 2, "completed_points": 1000},
            {"sprint_number": 2, "planned_points": 20, "completed_points": 0},
        ]}
        saved = copy.deepcopy(data)
        result = tool.analyze_sprint_health(data)
        self.assertEqual(result.dimension_scores["commitment_reliability"]["score"], 0)
        self.assertGreaterEqual(result.overall_score, 0)
        self.assertLessEqual(result.overall_score, 100)
        self.assertEqual(data, saved)
        expected = sum(value["score"] * tool.HEALTH_DIMENSIONS[key]["weight"]
                       for key, value in result.dimension_scores.items())
        self.assertEqual(result.overall_score, expected)

    def test_normal_scores_are_preserved(self):
        self.assertEqual(score([1, 1])["score"], 100)
        self.assertEqual(score([0, 0])["score"], 30)
        self.assertAlmostEqual(score([1, 0])["score"], 40 - 10 / math.sqrt(2))
        self.assertEqual(score([100, 100])["score"], 100)

    def test_floor_boundary(self):
        for value in [14, 15]:
            expected = max(0, 105 - value * 10 / math.sqrt(2))
            self.assertAlmostEqual(score([value, 0])["score"], expected)

    def test_nonnegative_pair_grid_is_bounded(self):
        values = [0, 0.1, 0.5, 0.7, 0.85, 0.95, 1, 1.5, 5, 10, 20, 100, 1000]
        for pair in itertools.product(values, repeat=2):
            with self.subTest(pair=pair):
                result = score(pair)
                self.assertGreaterEqual(result["score"], 0)
                self.assertLessEqual(result["score"], 100)

    def test_empty_input_contract_is_preserved(self):
        self.assertEqual(tool.score_commitment_reliability([]),
                         {"score": 0, "grade": "insufficient_data"})

    def test_json_and_text_cli_show_bounded_scores(self):
        data = {"sprints": [{"planned_points": 1, "completed_points": 500},
                            {"planned_points": 1, "completed_points": 0}]}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sprints.json"
            path.write_text(json.dumps(data))
            for fmt in ["json", "text"]:
                process = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", fmt],
                    capture_output=True, text=True, check=True)
                self.assertEqual(process.stderr, "")
                if fmt == "json":
                    result = json.loads(process.stdout)
                    self.assertEqual(result["dimension_scores"]["commitment_reliability"]["score"], 0)
                    self.assertGreaterEqual(result["overall_score"], 0)
                else:
                    self.assertIn("Score: 0.0/100 (Poor)", process.stdout)
                    self.assertNotIn("Score: -", process.stdout)


if __name__ == "__main__":
    unittest.main()

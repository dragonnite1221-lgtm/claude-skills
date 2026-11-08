"""Scope overdelivery must not inflate the normalized project health score."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / (
    "project-management/senior-pm/scripts/project_health_dashboard.py"
)
spec = importlib.util.spec_from_file_location("project_health_dashboard", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def record(**changes):
    return dict({"project_id": "P1", "project_name": "Project", "status": "active",
                 "planned_features": 10, "completed_features": 10,
                 "descoped_features": 5, "test_coverage": 1}, **changes)


class ScopeCompletionCapTests(unittest.TestCase):
    def test_descoping_does_not_inflate_health(self):
        project = tool.ProjectMetrics(record())
        result = tool.calculate_project_health_score(project)
        self.assertEqual(project.scope_health, 1)
        self.assertEqual(result["dimension_scores"]["scope"]["score"], 100)
        self.assertEqual(result["composite_score"], 100)

    def test_overdelivery_is_capped(self):
        for completed in [11, 20, 100, 10000]:
            with self.subTest(completed=completed):
                project = tool.ProjectMetrics(record(completed_features=completed, descoped_features=0))
                self.assertEqual(project.scope_health, 1)
                self.assertEqual(tool.calculate_project_health_score(project)["composite_score"], 100)

    def test_partial_and_exact_completion_are_preserved(self):
        for completed in range(11):
            project = tool.ProjectMetrics(record(completed_features=completed, descoped_features=0))
            self.assertAlmostEqual(project.scope_health, completed / 10)

    def test_added_and_removed_scope_use_effective_plan(self):
        project = tool.ProjectMetrics(record(added_features=10, descoped_features=0))
        self.assertEqual(project.scope_health, 0.5)
        project = tool.ProjectMetrics(record(added_features=10, descoped_features=5))
        self.assertAlmostEqual(project.scope_health, 2 / 3)
        for changes in [{"planned_features": 0}, {"descoped_features": 10},
                        {"descoped_features": 20}]:
            self.assertEqual(tool.ProjectMetrics(record(**changes)).scope_health, 1)

    def test_priority_weighting_is_not_capped(self):
        result = tool.calculate_project_health_score(tool.ProjectMetrics(record(priority="critical")))
        self.assertEqual(result["composite_score"], 100)
        self.assertEqual(result["adjusted_score"], 150)

    def test_portfolio_aggregate_and_input_preservation(self):
        data = {"projects": [record(), record(project_id="P2", descoped_features=0),
                             record(project_id="P3", status="completed")]}
        saved = copy.deepcopy(data)
        result = tool.analyze_portfolio_health(data)
        self.assertEqual(result.summary["active_projects"], 2)
        self.assertEqual(result.summary["portfolio_average_score"], 100)
        self.assertEqual(result.summary["portfolio_median_score"], 100)
        self.assertEqual(result.rag_status["rag_counts"], {"green": 2, "amber": 0, "red": 0})
        self.assertEqual(data, saved)

    def test_json_and_text_cli_show_bounded_scope_and_composite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "portfolio.json"
            path.write_text(json.dumps({"projects": [record()]}))
            for fmt in ["json", "text"]:
                process = subprocess.run(
                    [sys.executable, str(SCRIPT), str(path), "--format", fmt],
                    capture_output=True, text=True, check=True)
                self.assertEqual(process.stderr, "")
                if fmt == "json":
                    result = json.loads(process.stdout)
                    self.assertEqual(result["project_scores"][0]["dimension_scores"]["scope"]["score"], 100)
                    self.assertEqual(result["summary"]["portfolio_average_score"], 100)
                else:
                    self.assertIn("Portfolio Health Score: 100.0/100", process.stdout)
                    self.assertNotIn("120", process.stdout)


if __name__ == "__main__":
    unittest.main()

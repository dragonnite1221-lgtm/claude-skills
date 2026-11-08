"""Technical debt advice must compare required and current team sizes."""

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "c-level-advisor/cto-advisor/scripts/tech_debt_analyzer.py"
SPEC = importlib.util.spec_from_file_location("tech_debt_under_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def system(team_size, performance=90):
    return {
        "name": "Synthetic system", "team_size": team_size,
        "architecture": {"monolithic_design": 80},
        "code_quality": {"low_test_coverage": 80},
        "infrastructure": {"manual_deployments": 90},
        "security": {"outdated_dependencies": 100},
        "performance": {"slow_response_times": performance},
    }


def scaling(result):
    return [r for r in result["recommendations"] if r.startswith("Scale team to ")]


class TeamRecommendationTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MODULE.TechDebtAnalyzer()

    def test_default_team_without_actions_needs_no_growth(self):
        result = self.analyzer.analyze_system({})
        self.assertEqual(result["estimated_effort"]["total_story_points"], 0)
        self.assertEqual(scaling(result), [])

    def test_exact_effort_multiple_requires_growth(self):
        result = self.analyzer.analyze_system(system(4))
        self.assertEqual(result["estimated_effort"]["total_story_points"], 1000)
        self.assertEqual(result["estimated_effort"]["recommended_team_size"], 5)
        self.assertEqual(scaling(result), ["Scale team to 5 engineers"])

    def test_team_at_required_size_needs_no_growth(self):
        self.assertEqual(scaling(self.analyzer.analyze_system(system(5))), [])

    def test_larger_existing_team_needs_no_growth(self):
        result = self.analyzer.analyze_system(system(8))
        self.assertEqual(result["estimated_effort"]["recommended_team_size"], 8)
        self.assertEqual(scaling(result), [])

    def test_effort_just_above_boundary_requires_next_size(self):
        result = self.analyzer.analyze_system(system(5, performance=90.5))
        self.assertEqual(result["estimated_effort"]["total_story_points"], 1001)
        self.assertEqual(scaling(result), ["Scale team to 6 engineers"])

    def test_text_report_contains_required_growth(self):
        text = MODULE.analyze_technical_debt(system(4))
        self.assertIn("Recommended Team Size: 5", text)
        self.assertIn("Scale team to 5 engineers", text)

    def test_input_is_preserved(self):
        data = system(4)
        before = copy.deepcopy(data)
        self.analyzer.analyze_system(data)
        self.assertEqual(data, before)

    def test_private_helper_retains_default_team_argument(self):
        result = {"debt_level": "Low", "category_scores": {},
                  "estimated_effort": {"recommended_team_size": 5, "total_story_points": 0}}
        recommendations = self.analyzer._generate_recommendations(result)
        self.assertFalse(any(r.startswith("Scale team to ") for r in recommendations))


if __name__ == "__main__":
    unittest.main()

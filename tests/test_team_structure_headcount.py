"""Growth-stage teams must not allocate more people than the target."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/cto-advisor/scripts/team_scaling_calculator.py'
SPEC = importlib.util.spec_from_file_location('team_structure_tool', SCRIPT)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class TeamStructureHeadcountTests(unittest.TestCase):
    def setUp(self):
        self.calculator = TOOL.TeamScalingCalculator()

    def sizes(self, target):
        return [team['size'] for team in self.calculator._design_team_structure(target)['teams']]

    def test_first_growth_target(self):
        self.assertEqual(self.sizes(11), [6, 5])

    def test_one_person_remainder(self):
        self.assertEqual(self.sizes(13), [6, 6, 1])

    def test_final_growth_target(self):
        self.assertEqual(self.sizes(50), [6] * 8 + [2])

    def test_complete_teams_unchanged(self):
        for target in range(12, 49, 6):
            with self.subTest(target=target):
                self.assertEqual(self.sizes(target), [6] * (target // 6))

    def test_every_growth_target_is_conserved(self):
        for target in range(11, 51):
            with self.subTest(target=target):
                sizes = self.sizes(target)
                self.assertEqual(sum(sizes), target)
                self.assertTrue(all(1 <= size <= 6 for size in sizes))

    def test_team_names_and_focus_order_unchanged(self):
        teams = self.calculator._design_team_structure(25)['teams']
        self.assertEqual([t['name'] for t in teams], ['Team 1', 'Team 2', 'Team 3', 'Team 4', 'Team 5'])
        self.assertEqual([t['focus'] for t in teams], ['Platform', 'Product', 'Infrastructure', 'Growth', 'Platform'])

    def test_communication_paths_and_stage_unchanged(self):
        structure = self.calculator._design_team_structure(13)
        self.assertEqual(structure['organizational_model'], 'team_leads')
        self.assertEqual(structure['communication_paths'], 78)
        self.assertEqual(structure['management_layers'], 2)
        self.assertEqual(self.sizes(10), [10])

    def test_public_plan_preserves_target_headcount(self):
        plan = self.calculator.calculate_scaling_plan({'headcount': 10}, {'target_headcount': 13, 'timeline_quarters': 4})
        self.assertEqual(sum(t['size'] for t in plan['team_structure']['teams']), 13)
        self.assertEqual(plan['hiring_plan']['total_hires_needed'], 3)


if __name__ == '__main__':
    unittest.main()

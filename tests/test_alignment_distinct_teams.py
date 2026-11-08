import copy
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/strategic-alignment/scripts/alignment_checker.py'
SPEC = importlib.util.spec_from_file_location('alignment', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(counts):
    return {'company': {'name': 'Example', 'okrs': [{'id': 'C', 'objective': 'Goal'}]},
            'teams': [{'name': f'Team{i}', 'okrs': [{'id': f'{i}-{j}', 'objective': 'Support',
                       'parent_company_okr_id': 'C'} for j in range(n)]} for i, n in enumerate(counts)]}


class CoverageTests(unittest.TestCase):
    def test_one_team_four_okrs_not_overindexed(self):
        self.assertEqual(MODULE.detect_coverage_gaps(fixture([4]), {'C'})[1], [])

    def test_three_teams_many_okrs_not_overindexed(self):
        self.assertEqual(MODULE.detect_coverage_gaps(fixture([4, 3, 2]), {'C'})[1], [])

    def test_four_distinct_teams_order_and_raw_coverage(self):
        data = fixture([3, 2, 1, 4])
        before = copy.deepcopy(data)
        gaps, over, coverage = MODULE.detect_coverage_gaps(data, {'C'})
        self.assertEqual(gaps, [])
        self.assertEqual(over[0]['supporting_team_count'], 4)
        self.assertEqual(over[0]['supporting_teams'], ['Team0', 'Team1', 'Team2', 'Team3'])
        self.assertEqual(len(coverage['C']), 10)
        self.assertEqual(data, before)

    def test_zero_support_gap_unchanged(self):
        gaps, over, coverage = MODULE.detect_coverage_gaps(fixture([]), {'C'})
        self.assertEqual(gaps[0]['supporting_team_count'], 0)
        self.assertEqual(gaps[0]['supporting_teams'], [])
        self.assertEqual(over, [])
        self.assertEqual(dict(coverage), {})


if __name__ == '__main__':
    unittest.main()

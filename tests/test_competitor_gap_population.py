"""Competitor gap statistics must exclude the separately supplied own product."""
import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'product-team/competitive-teardown/scripts/competitive_matrix_builder.py'
BUILD = runpy.run_path(str(SCRIPT))['build_matrix']


def fixture(own=5, rivals=(3, 4)):
    return {'dimensions': ['ux'], 'your_product': {'name': 'Our Product', 'scores': {'ux': own}},
            'competitors': [{'name': f'Rival {i}', 'scores': {'ux': score}}
                            for i, score in enumerate(rivals)]}


def gap(data):
    return BUILD(copy.deepcopy(data))['gap_analysis']['gaps']['ux']


class CompetitorGapPopulationTests(unittest.TestCase):
    def test_leading_product_is_not_competitor_best(self):
        result = gap(fixture())
        self.assertEqual(result['competitor_avg'], 3.5)
        self.assertEqual(result['competitor_best'], 4)
        self.assertEqual(result['gap_to_avg'], 1.5)
        self.assertEqual(result['gap_to_best'], 1)

    def test_lagging_product_does_not_dilute_competitor_average(self):
        result = gap(fixture(1, (4, 5)))
        self.assertEqual(result['competitor_avg'], 4.5)
        self.assertEqual(result['competitor_best'], 5)
        self.assertEqual(result['gap_to_avg'], -3.5)
        self.assertEqual(result['gap_to_best'], -4)
        self.assertEqual(result['priority'], 'high')

    def test_average_threshold_status_uses_only_rivals(self):
        self.assertEqual(gap(fixture(4, (3,)))['status'], 'ahead')
        self.assertEqual(gap(fixture(3, (4,)))['status'], 'behind')
        self.assertEqual(gap(fixture(3, (3,)))['status'], 'parity')

    def test_competitor_baseline_does_not_depend_on_own_score(self):
        for own in [1, 2, 3, 4, 5]:
            with self.subTest(own=own):
                result = gap(fixture(own))
                self.assertEqual((result['competitor_avg'], result['competitor_best']), (3.5, 4))

    def test_same_name_rival_still_contributes(self):
        data = fixture(5, (4, 2))
        data['competitors'][0]['name'] = data['your_product']['name']
        result = gap(data)
        self.assertEqual((result['competitor_avg'], result['competitor_best']), (3, 4))
        self.assertEqual(result['gap_to_best'], 1)

    def test_ranking_still_includes_own_product_and_weights(self):
        result = BUILD(fixture(), {'ux': 2})
        self.assertEqual([x['name'] for x in result['scored_competitors']],
                         ['Our Product', 'Rival 1', 'Rival 0'])
        self.assertTrue(result['scored_competitors'][0]['is_you'])
        self.assertEqual(result['positioning']['your_rank'], 1)
        self.assertEqual(result['positioning']['total_competitors'], 3)
        self.assertEqual(result['weights'], {'ux': 2})

    def test_without_own_product_no_gap_section_is_added(self):
        data = fixture()
        del data['your_product']
        result = BUILD(data)
        self.assertNotIn('gap_analysis', result)
        self.assertEqual(len(result['scored_competitors']), 2)

    def test_real_cli_formats_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'competitors.json'
            path.write_text(json.dumps(fixture()), encoding='utf-8')
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            for fmt in ['json', 'text']:
                result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(path),
                                         '--format', fmt], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, '')
                if fmt == 'json':
                    value = json.loads(result.stdout)['gap_analysis']['gaps']['ux']
                    self.assertEqual(value['competitor_avg'], 3.5)
                    self.assertEqual(value['competitor_best'], 4)
                else:
                    self.assertIn('Avg=3.5, Lead=+1.5', result.stdout)
                self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))
            help_result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--help'],
                                         capture_output=True, text=True)
            self.assertEqual(help_result.returncode, 0)
            self.assertIn('Build competitive matrix', help_result.stdout)
        print('CLI invocations: 3')


if __name__ == '__main__':
    unittest.main()

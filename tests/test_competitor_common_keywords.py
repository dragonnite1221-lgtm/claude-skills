import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'marketing-skill/app-store-optimization/scripts/competitor_analyzer.py'
spec = importlib.util.spec_from_file_location('competitor_common', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CommonKeywordTests(unittest.TestCase):
    def compare(self, titles):
        return module.CompetitorAnalyzer('Productivity').compare_competitors(
            [{'app_name': str(i), 'title': title} for i, title in enumerate(titles)])

    def test_repetition_in_one_app_is_not_common(self):
        for titles in [['alpha alpha'], ['alpha alpha', 'bravo'], ['ALPHA alpha', 'bravo']]:
            with self.subTest(titles=titles):
                self.assertNotIn('alpha', self.compare(titles)['common_keywords'])

    def test_cross_competitor_frequency_controls_order(self):
        result = self.compare(['alpha alpha alpha bravo', 'alpha bravo', 'bravo'])
        self.assertEqual(result['common_keywords'], ['bravo', 'alpha'])

    def test_raw_primary_keywords_are_preserved(self):
        result = self.compare(['alpha alpha', 'bravo'])
        first = next(a for a in result['ranked_competitors'] if a['app_name'] == '0')
        self.assertEqual(first['keyword_strategy']['primary_keywords'], ['alpha', 'alpha'])

    def test_unique_titles_keep_first_seen_tie_order(self):
        self.assertEqual(self.compare(['bravo alpha', 'alpha bravo'])['common_keywords'],
                         ['bravo', 'alpha'])


if __name__ == '__main__':
    unittest.main()

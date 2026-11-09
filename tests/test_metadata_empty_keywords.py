import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'marketing-skill/app-store-optimization/scripts/metadata_optimizer.py'
spec = importlib.util.spec_from_file_location('metadata_empty', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EmptyKeywordsTests(unittest.TestCase):
    def test_empty_field_reports_zero(self):
        for keywords, title in [([], ''), ([''], ''), (['  '], ''), (['todo'], 'Todo'), (['x' * 101], '')]:
            with self.subTest(keywords=keywords, title=title):
                result = module.MetadataOptimizer().optimize_keyword_field(keywords, title)
                self.assertEqual(result['keyword_field'], '')
                self.assertEqual(result['keywords_included'], [])
                self.assertEqual(result['keywords_count'], 0)

    def test_nonempty_field(self):
        result = module.MetadataOptimizer().optimize_keyword_field(['todo', 'planner'])
        self.assertEqual(result['keyword_field'], 'todo,planner')
        self.assertEqual(result['keywords_included'], ['todo', 'planner'])
        self.assertEqual(result['keywords_count'], 2)

    def test_google_unchanged(self):
        self.assertIn('error', module.MetadataOptimizer('google').optimize_keyword_field([]))

    def test_convenience_empty(self):
        result = module.optimize_app_metadata('apple', {'name': 'Demo'}, [])
        self.assertEqual(result['keyword_field']['keywords_count'], 0)
        self.assertEqual(result['keyword_field']['keywords_included'], [])


if __name__ == '__main__':
    unittest.main()

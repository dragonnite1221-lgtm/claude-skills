import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'engineering-team/tdd-guide/scripts/metrics_calculator.py'
spec = importlib.util.spec_from_file_location('tdd_metrics', P)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PythonCountTests(unittest.TestCase):
    def setUp(self):
        self.calculator = module.MetricsCalculator()

    def test_one_definition_counted_once(self):
        result = self.calculator.calculate_test_quality('def test_returns_value():\n    assert True\n')
        self.assertEqual(result['total_tests'], 1)
        self.assertEqual(result['avg_assertions_per_test'], 1)

    def test_multiple_definitions_and_methods(self):
        code = 'def test_one():\n    assert True\nclass Tests:\n    def test_two(self):\n        assert True\n'
        self.assertEqual(self.calculator.calculate_test_quality(code)['total_tests'], 2)

    def test_roulette_threshold(self):
        code = 'def test_six():\n' + '    assert True\n' * 6
        result = self.calculator.calculate_test_quality(code)
        self.assertEqual(result['avg_assertions_per_test'], 6)
        self.assertIn('assertion_roulette', [s['smell'] for s in result['test_smells']])

    def test_other_framework_counts_unchanged(self):
        for code, expected in [('it("a", () => {}); test("b", () => {});', 2), ('@Test public void check() {}', 1), ('', 1)]:
            with self.subTest(code=code):
                self.assertEqual(self.calculator._count_test_functions(code), expected)


if __name__ == '__main__':
    unittest.main()

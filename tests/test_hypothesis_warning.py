import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/statistical-analyst/scripts/hypothesis_tester.py'
spec = importlib.util.spec_from_file_location('hypothesis_warning', SCRIPT)
tester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tester)


class WarningTests(unittest.TestCase):
    def test_chi_square_warning_is_not_a_verdict(self):
        for observed, expected in [([1, 9], [2, 8]), ([3, 3, 4], [4, 3, 3]), ([10, 0], [1, 9])]:
            with self.subTest(expected=expected):
                result = tester.chi2_test(observed, expected, .05)
                text = tester.verdict(result)
                self.assertIn(result['warning'], text)
                self.assertIn(result['suggestion'], text)
                for fabricated in ['p-value:', 'VERDICT:', 'statistically significant', 'Effect:']:
                    self.assertNotIn(fabricated, text)

    def test_warning_without_suggestion_and_error_precedence(self):
        self.assertEqual(tester.verdict({'warning': 'Caution'}), 'WARNING: Caution')
        self.assertEqual(tester.verdict({'error': 'Bad', 'warning': 'Caution'}), 'ERROR: Bad')

    def test_successful_result_still_reports(self):
        result = tester.chi2_test([20, 30], [25, 25], .05)
        text = tester.verdict(result)
        self.assertIn('p-value:', text)
        self.assertIn('VERDICT:', text)
        self.assertNotIn('WARNING:', text)

    def test_cli_text_and_json(self):
        args = [sys.executable, str(SCRIPT), '--test', 'chi2', '--observed', '1,9', '--expected', '2,8']
        text = subprocess.run(args, capture_output=True, text=True, check=True)
        result = subprocess.run(args + ['--format', 'json'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn(data['warning'], text.stdout)
        self.assertIn(data['suggestion'], text.stdout)
        self.assertNotIn('p-value:', text.stdout)
        self.assertEqual(set(data), {'warning', 'suggestion'})


if __name__ == '__main__':
    unittest.main()

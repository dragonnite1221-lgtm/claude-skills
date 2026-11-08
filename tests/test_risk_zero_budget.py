"""An explicit zero mitigation budget is not an omitted option."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/ciso-advisor/scripts/risk_quantifier.py'


def run(*args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True, check=True).stdout


class ZeroBudgetTests(unittest.TestCase):
    def test_integer_zero(self):
        text = run('--budget', '0')
        self.assertIn('BUDGET ALLOCATION — $0', text)
        self.assertIn('No actionable mitigations fit within budget.', text)

    def test_decimal_zero(self):
        self.assertIn('BUDGET ALLOCATION — $0', run('--budget', '0.0'))

    def test_scientific_zero(self):
        self.assertIn('BUDGET ALLOCATION — $0', run('--budget', '0e2'))

    def test_omitted_budget(self):
        self.assertNotIn('BUDGET ALLOCATION', run())

    def test_small_positive_budget(self):
        text = run('--budget', '1')
        self.assertIn('BUDGET ALLOCATION — $1', text)
        self.assertIn('No actionable mitigations fit within budget.', text)

    def test_funded_budget(self):
        text = run('--budget', '200000')
        self.assertIn('BUDGET ALLOCATION — $200,000', text)
        self.assertNotIn('No actionable mitigations fit within budget.', text)

    def test_json_precedence_unchanged(self):
        data = json.loads(run('--json', '--budget', '0'))
        self.assertEqual(set(data), {'generated', 'summary', 'risks'})
        self.assertEqual(data['summary']['total_risks'], len(data['risks']))

    def test_board_precedence_unchanged(self):
        text = run('--board', '--budget', '0')
        self.assertIn('BOARD SECURITY REPORT', text)
        self.assertNotIn('BUDGET ALLOCATION', text)


if __name__ == '__main__':
    unittest.main()

"""Normal-tail symmetry avoids cancellation for small positive alpha."""
import math
from pathlib import Path
import runpy
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'product-team/experiment-designer/scripts/sample_size_calculator.py'
CALCULATE = runpy.run_path(str(SCRIPT))['required_sample_size_per_group']


def upper_quantile(tail):
    """Independent inverse using erfc, avoiding the implementation's inv_cdf."""
    lower, upper = -40.0, 40.0
    for _ in range(160):
        middle = (lower + upper) / 2
        if math.erfc(middle / math.sqrt(2)) / 2 > tail:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2


class SmallAlphaTests(unittest.TestCase):
    cli_count = 0

    def cli(self, *args):
        type(self).cli_count += 1
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def test_documented_normal_estimates(self):
        self.assertEqual(CALCULATE(.12, .14, .05, .8), 4439)
        self.assertEqual(CALCULATE(.10, .115, .05, .8), 6694)

    def test_extreme_alpha_matches_erfc_oracle(self):
        for alpha in [1e-16, 1e-20, 1e-100, 1e-300]:
            with self.subTest(alpha=alpha):
                z = upper_quantile(alpha / 2) + upper_quantile(1 - .8)
                expected = math.ceil(2 * .13 * .87 * z ** 2 / (.14 - .12) ** 2)
                self.assertEqual(CALCULATE(.12, .14, alpha, .8), expected)

    def test_known_tiny_alpha_result(self):
        self.assertEqual(CALCULATE(.12, .14, 1e-20, .8), 58578)

    def test_smaller_alpha_requires_more_samples(self):
        counts = [CALCULATE(.12, .14, a, .8) for a in [.05, .01, 1e-10, 1e-20]]
        self.assertTrue(all(a < b for a, b in zip(counts, counts[1:])))

    def test_group_exchange_symmetry(self):
        for alpha in [.05, 1e-20, 1e-300]:
            self.assertEqual(CALCULATE(.12, .14, alpha, .8),
                             CALCULATE(.14, .12, alpha, .8))

    def test_cli_accepts_small_alpha(self):
        for alpha in ['1e-16', '1e-20', '1e-100', '1e-300']:
            with self.subTest(alpha=alpha):
                output = self.cli('--baseline-rate', '.12', '--mde', '.02',
                                  '--mde-type', 'absolute', '--alpha', alpha,
                                  '--daily-samples', '100')
                values = dict(line.split(': ', 1) for line in output.splitlines()[1:])
                per_group = int(values['n_per_group'])
                self.assertGreater(per_group, 0)
                self.assertEqual(int(values['n_total']), per_group * 2)
                self.assertEqual(int(values['estimated_days_at_daily_samples_100']),
                                 (per_group * 2 + 99) // 100)

    def test_cli_ordinary_absolute_and_relative(self):
        for mode, mde in [('absolute', '.015'), ('relative', '.15')]:
            output = self.cli('--baseline-rate', '.1', '--mde', mde,
                              '--mde-type', mode, '--daily-samples', '73')
            self.assertIn('n_per_group: 6694\n', output)
            self.assertIn('estimated_days_at_daily_samples_73: 184\n', output)

    def test_help(self):
        self.assertIn('Compute sample size', self.cli('--help'))

    @classmethod
    def tearDownClass(cls):
        print(f'CLI invocations: {cls.cli_count}')


if __name__ == '__main__':
    unittest.main()

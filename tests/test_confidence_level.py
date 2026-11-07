import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/statistical-analyst/scripts/confidence_interval.py'
spec = importlib.util.spec_from_file_location('confidence_level', SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class ConfidenceLevelTests(unittest.TestCase):
    def test_invalid_proportion_confidence(self):
        for value in [-1, 0, 1, 2, float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=value):
                self.assertIn('error', ci.wilson_interval(100, 40, value))

    def test_invalid_mean_confidence(self):
        for value in [-1, 0, 1, 2, float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=value):
                self.assertIn('error', ci.mean_interval(100, 40, 2, value))

    def test_valid_reference_intervals(self):
        result = ci.wilson_interval(100, 50, .95)
        self.assertEqual((result['lower'], result['upper']), (.403832, .596168))
        result = ci.mean_interval(100, 40, 2, .95)
        self.assertEqual((result['lower'], result['upper']), (39.608007, 40.391993))

    def test_cli_errors_without_tracebacks(self):
        for kind, extra in [('mean', ['--mean', '40', '--std', '2']), ('proportion', ['--x', '40'])]:
            for level in ['-1', '0', '1', '2', 'nan', 'inf', '-inf']:
                for output in ['json', 'text']:
                    with self.subTest(kind=kind, level=level, output=output):
                        p = subprocess.run([sys.executable, str(SCRIPT), '--type', kind, '--n', '100', '--confidence='+level, '--format', output, *extra], capture_output=True, text=True)
                        if output == 'json':
                            self.assertIn('error', json.loads(p.stdout))
                        else:
                            self.assertEqual(p.returncode, 1)
                            self.assertIn('confidence must be', p.stderr)
                        self.assertNotIn('Traceback', p.stderr)


if __name__ == '__main__':
    unittest.main()

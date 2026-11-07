import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/statistical-analyst/scripts/sample_size_calculator.py'
spec = importlib.util.spec_from_file_location('sample_zero_effect', SCRIPT)
calculator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calculator)


class ZeroEffectTests(unittest.TestCase):
    def test_zero_effect_rejected(self):
        for baseline in [.001, .05, .5, .99]:
            for mde in [0., -0., 1e-20, -1e-20]:
                with self.subTest(baseline=baseline, mde=mde):
                    with self.assertRaisesRegex(ValueError, 'zero effect'):
                        calculator.sample_size_proportion(baseline, mde, .05, .8)

    def test_cli_fails_cleanly(self):
        for fmt in ['text', 'json']:
            result = subprocess.run([sys.executable, str(SCRIPT), '--test', 'proportion', '--baseline', '.05', '--mde', '0', '--format', fmt], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Error:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(result.stdout, '')

    def test_table_marks_undefined_cells(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            calculator.print_table('proportion', .05, 0, .05, None, None)
        self.assertEqual(output.getvalue().count('N/A'), 30)

    def test_valid_increase_and_decrease(self):
        self.assertEqual(calculator.sample_size_proportion(.05, .2, .05, .8), 8155)
        self.assertGreater(calculator.sample_size_proportion(.05, -.2, .05, .8), 0)


if __name__ == '__main__':
    unittest.main()

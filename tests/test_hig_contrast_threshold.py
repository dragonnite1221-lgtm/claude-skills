"""Keep full contrast precision for decisions, rounding only display values."""
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'product-team/apple-hig-expert/scripts/hig_checker.py'
CHECK = runpy.run_path(str(SCRIPT))['check_contrast']


class ContrastThresholdTests(unittest.TestCase):
    cli_count = 0

    def cli(self, *args):
        type(self).cli_count += 1
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def batch(self, checks):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'elements.json'
            path.write_text(json.dumps({'checks': checks}), encoding='utf-8')
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            result = json.loads(self.cli('batch', str(path)))
            self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))
        return result

    def test_unrounded_boundary_ratios(self):
        examples = [('#168700', '#000000', 4.499703792321153),
                    ('#6e7978', '#ffffff', 4.4975956603938485)]
        for fg, bg, expected in examples:
            with self.subTest(fg=fg, bg=bg):
                self.assertAlmostEqual(CHECK(fg, bg), expected, places=12)
                self.assertLess(CHECK(fg, bg), 4.5)

    def test_ratio_is_symmetric(self):
        for fg, bg in [('#168700', '#000000'), ('#6e7978', '#ffffff'),
                       ('#102030', '#abcdef')]:
            with self.subTest(fg=fg, bg=bg):
                self.assertEqual(CHECK(fg, bg), CHECK(bg, fg))

    def test_extreme_and_identical_colors(self):
        self.assertEqual(CHECK('#000000', '#ffffff'), 21.0)
        for color in ['#000000', '#ffffff', '#168700']:
            self.assertEqual(CHECK(color, color), 1.0)

    def test_cli_rejects_rounding_boundary_both_directions(self):
        for fg, bg in [('#168700', '#000000'), ('#6e7978', '#ffffff')]:
            for pair in [(fg, bg), (bg, fg)]:
                with self.subTest(pair=pair):
                    output = self.cli('contrast', *pair)
                    self.assertIn('Contrast Ratio: 4.5 [FAILED]', output)
                    self.assertIn('Recommendation:', output)

    def test_cli_preserves_ordinary_display(self):
        cases = [('#000000', '#ffffff', '21.0 [PASSED]'),
                 ('#777777', '#ffffff', '4.48 [FAILED]'),
                 ('#168700', '#168700', '1.0 [FAILED]')]
        for fg, bg, expected in cases:
            with self.subTest(fg=fg, bg=bg):
                self.assertIn('Contrast Ratio: ' + expected, self.cli('contrast', fg, bg))

    def test_batch_flags_both_boundary_pairs(self):
        result = self.batch([
            {'type': 'contrast', 'fg': '#168700', 'bg': '#000000', 'name': 'green'},
            {'type': 'contrast', 'fg': '#ffffff', 'bg': '#6e7978', 'name': 'gray'},
        ])
        self.assertEqual(result, {'score': 80, 'violations': [
            'Contrast 4.5 fails for green', 'Contrast 4.5 fails for gray']})

    def test_batch_preserves_other_checks(self):
        result = self.batch([
            {'type': 'target', 'w': 44, 'h': 44},
            {'type': 'target', 'w': 43, 'h': 44, 'name': 'small'},
            {'type': 'contrast', 'fg': '#000000', 'bg': '#ffffff'},
            {'type': 'contrast', 'fg': '#000000', 'bg': '#000000'},
        ])
        self.assertEqual(result, {'score': 80, 'violations': [
            'Target 43x44 small for small', 'Contrast 1.0 fails for element']})

    def test_help_remains_available(self):
        self.assertIn('Apple HIG Compliance Checker', self.cli('--help'))

    @classmethod
    def tearDownClass(cls):
        print(f'CLI invocations: {cls.cli_count}')


if __name__ == '__main__':
    unittest.main()

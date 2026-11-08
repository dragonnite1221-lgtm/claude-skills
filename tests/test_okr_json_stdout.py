"""The OKR CLI keeps machine-readable JSON separate from notices."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/coo-advisor/scripts/okr_tracker.py'
BANNER = 'No input file specified — running with sample data.\n\n'


def invoke(*args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                          capture_output=True, text=True, check=False)


class OkrJsonStdoutTests(unittest.TestCase):
    def test_sample_json_is_one_clean_document(self):
        result = invoke('--format', 'json', '--quarter-progress', '0.5')
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['objectives']), 3)
        self.assertEqual(result.stderr, BANNER)
        self.assertTrue(result.stdout.startswith('{'))

    def test_short_format_alias_is_clean(self):
        result = invoke('-f', 'json', '--quarter-progress', '0.5')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('company_score', json.loads(result.stdout))
        self.assertEqual(result.stderr, BANNER)

    def test_text_mode_keeps_notice_on_stdout(self):
        for args in ([], ['--format', 'text']):
            result = invoke(*args, '--quarter-progress', '0.5')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith(BANNER))
            self.assertIn('OKR TRACKING REPORT', result.stdout)
            self.assertEqual(result.stderr, '')

    def test_custom_json_input_has_no_sample_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_text(json.dumps({'company_okrs': {'name': 'Custom', 'objectives': []}}))
            result = invoke('--input', str(path), '--format', 'json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['objectives'], [])
        self.assertEqual(result.stderr, '')

    def test_json_output_file_still_contains_only_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            result = invoke('--format', 'json', '--output', str(path), '--quarter-progress', '0.5')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(path.read_text())['objectives']), 3)
            self.assertEqual(result.stdout, f'Report written to: {path}\n')
            self.assertEqual(result.stderr, BANNER)

    def test_quarter_boundaries_keep_stdout_parseable(self):
        for progress in ('0', '0.5', '1'):
            with self.subTest(progress=progress):
                result = invoke('--format', 'json', '--quarter-progress', progress)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsInstance(json.loads(result.stdout)['at_risk_count'], int)

    def test_help_does_not_emit_sample_notice(self):
        result = invoke('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('usage:', result.stdout)
        self.assertNotIn(BANNER, result.stdout)
        self.assertEqual(result.stderr, '')

    def test_invalid_input_json_keeps_error_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'broken.json'
            path.write_text('{')
            result = invoke('--input', str(path), '--format', 'json')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Error: Invalid JSON:', result.stderr)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()

"""PMF JSON mode must emit a single JSON document on stdout."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/cpo-advisor/scripts/pmf_scorer.py'
SPEC = importlib.util.spec_from_file_location('pmf_json_tool', SCRIPT)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)
BANNER = 'No input file provided — running with sample data.'


def run(*args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True, check=True)


class PmfJsonStdoutTests(unittest.TestCase):
    def test_sample_stdout_is_json(self):
        output = json.loads(run('--json').stdout)
        self.assertEqual(output['product_name'], 'Acme SaaS')

    def test_sample_notice_is_stderr(self):
        result = run('--json')
        self.assertNotIn(BANNER, result.stdout)
        self.assertEqual(result.stderr, BANNER + '\n\n')

    def test_default_text_notice_unchanged(self):
        result = run()
        self.assertTrue(result.stdout.startswith(BANNER + '\n\n'))
        self.assertEqual(result.stderr, '')

    def test_sample_scoring_unchanged(self):
        output = json.loads(run('--json').stdout)
        expected = TOOL.run(TOOL.sample_data())
        self.assertEqual(output['overall_score'], round(expected['overall'], 4))
        self.assertEqual(output['status'], expected['status'])
        for dim, data in output['dimensions'].items():
            self.assertEqual(data['score'], round(expected['dim_scores'][dim], 4))
            self.assertEqual(data['findings'], expected['dim_findings'][dim])

    def test_explicit_input_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            path.write_text(json.dumps(TOOL.sample_data()))
            result = run('--input', str(path), '--json')
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout), json.loads(run('--json').stdout))

    def test_short_input_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            path.write_text('{}')
            result = run('-i', str(path), '--json')
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout)['overall_score'], 0)

    def test_explicit_text_has_no_sample_notice(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            path.write_text('{}')
            result = run('-i', str(path))
        self.assertNotIn(BANNER, result.stdout)
        self.assertEqual(result.stderr, '')

    def test_help_is_unchanged_output_channel(self):
        result = run('--help')
        self.assertIn('--json', result.stdout)
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()

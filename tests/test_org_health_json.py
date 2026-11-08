import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/org-health-diagnostic/scripts/health_scorer.py'


class JsonOutputTests(unittest.TestCase):
    def run_cli(self, args, stdin=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                              capture_output=True, text=True, check=True)

    def test_sample_json_is_standalone(self):
        result = self.run_cli(['--json'])
        data = json.loads(result.stdout)
        self.assertEqual(data['stage'], 'series_a')
        self.assertEqual(len(data['dimensions']), 8)
        self.assertIn('ORG HEALTH DIAGNOSTIC', result.stderr)

    def test_all_stage_aliases(self):
        for alias, stage in [('seed', 'seed'), ('a', 'series_a'), ('b', 'series_b'), ('c', 'series_c')]:
            with self.subTest(alias=alias):
                self.assertEqual(json.loads(self.run_cli(['--stage', alias, '--json']).stdout)['stage'], stage)

    def test_interactive_json_keeps_prompts_off_stdout(self):
        result = self.run_cli(['-i', '--json'], 'Synthetic\nseed\n' + '\n' * 40)
        data = json.loads(result.stdout)
        self.assertEqual(data['stage'], 'seed')
        self.assertIsNone(data['overall_score'])
        self.assertIn('Company name:', result.stderr)

    def test_text_default(self):
        result = self.run_cli([])
        self.assertIn('DIMENSION SCORES', result.stdout)
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()

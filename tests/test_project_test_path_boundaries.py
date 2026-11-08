"""Test discovery must match conventional path components, not substrings."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'product-team/spec-to-repo/scripts/validate_project.py'
CHECK = runpy.run_path(str(SCRIPT))['check_tests']


class TestPathBoundariesTests(unittest.TestCase):
    cli_count = 0

    def check(self, paths):
        root = os.path.abspath('synthetic-project')
        files = [os.path.join(root, *path.split('/')) for path in paths]
        return CHECK(files, root)

    def cli(self, *args):
        type(self).cli_count += 1
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                              capture_output=True, text=True, check=False)

    def test_lookalike_filenames_and_directories_are_not_tests(self):
        for path in ['latest_module.py', 'src/contest_results.py', 'contest/main.py',
                     'contests/main.py', 'prospectspec/main.py', 'not__tests__/main.py',
                     'src/latest/worker.ts', 'src/main.py']:
            with self.subTest(path=path):
                self.assertEqual(self.check([path])['status'], 'FAIL')

    def test_test_prefix_cannot_span_directories(self):
        for path in ['test_tools/main.py', 'src/test_helpers/runtime.py',
                     'test_support/nested/service.py']:
            with self.subTest(path=path):
                self.assertEqual(self.check([path])['status'], 'FAIL')

    def test_conventional_test_filenames_are_recognized(self):
        filenames = ['test_api.py', 'api_test.py', 'api.test.js', 'api.test.jsx',
                     'api.test.ts', 'api.test.tsx', 'api.spec.js', 'api.spec.jsx',
                     'api.spec.ts', 'api.spec.tsx', 'api_test.go', 'api_test.rs', 'api_test.dart']
        for filename in filenames:
            for prefix in ['', 'src/nested/']:
                with self.subTest(path=prefix + filename):
                    self.assertEqual(self.check([prefix + filename])['status'], 'PASS')

    def test_exact_test_directories_are_recognized(self):
        for directory in ['test', 'tests', 'spec', '__tests__']:
            for prefix in ['', 'src/nested/']:
                path = prefix + directory + '/nested/check.rb'
                with self.subTest(path=path):
                    self.assertEqual(self.check([path])['status'], 'PASS')

    def test_false_match_does_not_hide_later_real_test(self):
        result = self.check(['latest_module.py', 'contest/main.py', 'src/test_api.py'])
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['message'], 'Test file found: ' + os.path.join('src', 'test_api.py'))

    def test_windows_separator_normalization_without_changing_message(self):
        for path, status in [(r'src\tests\check.rb', 'PASS'),
                             (r'src\contest\main.py', 'FAIL'),
                             (r'src\test_tools\main.py', 'FAIL')]:
            with patch('os.path.relpath', return_value=path), patch.object(os, 'sep', '\\'):
                result = CHECK(['unused'], 'unused')
            self.assertEqual(result['status'], status)
            if status == 'PASS':
                self.assertEqual(result['message'], 'Test file found: ' + path)

    def test_cli_full_validation_and_input_preservation(self):
        for filename, expected_code in [('latest_module.py', 1), ('test_api.py', 0)]:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'README.md').write_text('A complete generated application with documented setup and usage.\n')
                (root / '.gitignore').write_text('build/\n')
                (root / 'package.json').write_text('{}\n')
                (root / filename).write_text('VALUE = 1\n')
                before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.iterdir()}
                for fmt in ['json', 'text']:
                    for strict in [[], ['--strict']]:
                        result = self.cli(str(root), '--format', fmt, *strict)
                        self.assertEqual(result.returncode, expected_code, result.stderr)
                        self.assertEqual(result.stderr, '')
                        if fmt == 'json':
                            report = json.loads(result.stdout)
                            check = next(c for c in report['checks'] if c['name'] == 'tests')
                            self.assertEqual(check['status'], 'PASS' if expected_code == 0 else 'FAIL')
                            self.assertTrue(all(c['status'] == 'PASS' for c in report['checks'] if c['name'] != 'tests'))
                        else:
                            self.assertIn('[PASS] tests:' if expected_code == 0 else '[FAIL] tests:', result.stdout)
                        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.iterdir()})

    def test_help(self):
        result = self.cli('--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Validate a generated project', result.stdout)

    @classmethod
    def tearDownClass(cls):
        print(f'CLI invocations: {cls.cli_count}')


if __name__ == '__main__':
    unittest.main()

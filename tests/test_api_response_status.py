"""Regression coverage for HTTP success codes and OpenAPI response ranges."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/api-design-reviewer/scripts/api_linter.py'
SPEC = importlib.util.spec_from_file_location('api_response_status_linter', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def spec(responses):
    return {'openapi': '3.0.3', 'info': {'title': 'Files', 'version': '1.0.0',
            'description': 'File API', 'contact': {}}, 'servers': [{'url': '/v1'}],
            'components': {}, 'paths': {'/files': {'get': {'summary': 'Read files',
            'description': 'Read files', 'responses': responses}}}}


class ResponseStatusTests(unittest.TestCase):
    def issues(self, *codes):
        linter = MODULE.APILinter()
        return linter.lint_openapi_spec(spec({code: {'description': 'Response'}
                                           for code in codes})).issues

    def test_all_three_digit_success_codes(self):
        for code in ('200', '201', '202', '203', '204', '205', '206', '207', '208', '226', '299'):
            with self.subTest(code=code):
                issues = self.issues(code, '400')
                self.assertFalse([i for i in issues if i.severity == 'error'])

    def test_openapi_response_ranges(self):
        for code in ('1XX', '2XX', '3XX', '4XX', '5XX'):
            with self.subTest(code=code):
                issues = self.issues('2XX', '4XX', code)
                self.assertFalse([i for i in issues if i.severity == 'error'])
                self.assertFalse([i for i in issues if 'Uncommon status code' in i.message])

    def test_invalid_ranges_do_not_become_successes(self):
        for code in ('2xx', '2X0', '20X', '0XX', '6XX', '2XXX'):
            with self.subTest(code=code):
                errors = [i.message for i in self.issues(code, '400') if i.severity == 'error']
                self.assertTrue(any('Invalid status code' in message for message in errors))
                self.assertTrue(any('Missing success response' in message for message in errors))

    def test_missing_success_and_method_advice_preserved(self):
        self.assertTrue(any('Missing success response' in i.message for i in self.issues('404', 'default')))
        self.assertTrue(any('Uncommon status code 206' in i.message for i in self.issues('206', '400')))
        self.assertFalse([i for i in self.issues('200', '400') if i.severity == 'error'])

    def test_cli_accepts_partial_content_and_ranges(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'api.json'
            for codes in [('206', '400'), ('2XX', '4XX'), ('200', '400')]:
                with self.subTest(codes=codes):
                    path.write_text(json.dumps(spec({code: {'description': 'Response'} for code in codes})))
                    result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--format', 'json'],
                                            text=True, capture_output=True, check=False)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)['summary']['errors'], 0)


if __name__ == '__main__':
    unittest.main()

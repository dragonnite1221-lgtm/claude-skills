"""Script failures gate reviews while PARTIAL stays a warning."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/required-skill-checks.py'
SPEC = importlib.util.spec_from_file_location('required_skill_checks', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class RequiredSkillChecksTest(unittest.TestCase):
    def test_script_status_and_exit_contract(self):
        structure = {'overall_score': 95, 'compliance_level': 'EXCELLENT', 'checks': {'required': {'passed': True}}, 'errors': []}
        security = {'verdict': 'PASS', 'summary': {'critical': 0, 'high': 0}}
        passed = {'total_scripts': 1, 'passed': 1, 'partial': 0, 'failed': 0, 'no_tests': 0, 'overall_status': 'PASS'}
        partial = {**passed, 'passed': 0, 'partial': 1, 'overall_status': 'PARTIAL'}
        failed = {**passed, 'passed': 0, 'failed': 1, 'overall_status': 'FAIL'}
        cases = [
            (0, passed, [], 'PASS', '1/1 PASS'),
            (1, partial, [], 'PASS', '0/1 PARTIAL'),
            (2, failed, [], 'FAIL', '0/1 FAIL'),
            (0, failed, [], 'FAIL', '0/1 FAIL'),
            (2, passed, [], 'FAIL', '1/1 PASS'),
            (0, partial, [], 'FAIL', '0/1 PARTIAL'),
            (0, passed, ['crashed'], 'FAIL', '1/1 PASS'),
            (130, passed, [], 'FAIL', '1/1 PASS'),
            (0, {}, [], 'FAIL', 'ERROR'),
            (0, {**passed, 'passed': '1'}, [], 'FAIL', 'ERROR'),
        ]
        with tempfile.TemporaryDirectory() as root:
            skill = Path(root)
            (skill / 'scripts').mkdir()
            (skill / 'scripts/example.py').touch()
            for code, summary, errors, expected, label in cases:
                with self.subTest(code=code, summary=summary, errors=errors):
                    results = [(0, structure), (code, {'summary': summary, 'global_errors': errors}), (0, security)]
                    with patch.object(MODULE, 'run_json', side_effect=results):
                        actual = MODULE.evaluate(str(skill))
                    self.assertEqual(actual[-1], expected)
                    self.assertEqual(actual[1], label)

    def test_structure_matches_producer_acceptance(self):
        security = {'verdict': 'PASS', 'summary': {'critical': 0, 'high': 0}}
        with tempfile.TemporaryDirectory() as root:
            for code, score, errors, expected in [(0, 60, [], 'PASS'), (0, 59, [], 'FAIL'), (1, 95, [], 'FAIL'), (0, 95, ['invalid'], 'FAIL')]:
                structure = {'overall_score': score, 'compliance_level': 'ACCEPTABLE', 'checks': {'optional': {'passed': False}}, 'errors': errors}
                with self.subTest(code=code, score=score, errors=errors), patch.object(MODULE, 'run_json', side_effect=[(code, structure), (0, security)]):
                    self.assertEqual(MODULE.evaluate(root)[-1], expected)

    def test_malformed_json_fails_closed(self):
        from subprocess import CompletedProcess
        for output in ('not JSON', '{} trailing junk'):
            with self.subTest(output=output), patch.object(MODULE.subprocess, 'run', return_value=CompletedProcess([], 0, output, '')):
                self.assertEqual(MODULE.run_json(['tester']), (-1, {}))

if __name__ == '__main__':
    unittest.main()

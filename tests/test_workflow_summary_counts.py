"""Workflow summaries must count the severities used in their findings."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-management/jira-expert/scripts/workflow_validator.py'
SPEC = importlib.util.spec_from_file_location('workflow_summary_counts', SCRIPT)
WORKFLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORKFLOW)


def basic_workflow():
    return {'states': ['Open', 'Done'], 'initial_state': 'Open',
            'transitions': [{'from': 'Open', 'to': 'Done', 'name': 'Complete'}]}


class WorkflowSummaryTests(unittest.TestCase):
    def assert_summary(self, result):
        expected = {key: sum(f['severity'] == severity for f in result['findings'])
                    for key, severity in [('errors', 'error'), ('warnings', 'warning'), ('info', 'info')]}
        self.assertEqual(result['summary'], expected)
        self.assertEqual(sum(result['summary'].values()), len(result['findings']))

    def test_healthy_workflow(self):
        result = WORKFLOW.validate_workflow(basic_workflow())
        self.assertEqual(result['summary'], {'errors': 0, 'warnings': 0, 'info': 0})
        self.assertEqual(result['health_score'], 100)

    def test_errors_are_counted(self):
        data = basic_workflow()
        data['transitions'] = []
        result = WORKFLOW.validate_workflow(data)
        self.assertGreater(result['summary']['errors'], 0)
        self.assert_summary(result)

    def test_warnings_are_counted(self):
        data = basic_workflow()
        data['transitions'] *= 2
        result = WORKFLOW.validate_workflow(data)
        self.assertEqual(result['summary'], {'errors': 0, 'warnings': 1, 'info': 0})
        self.assertEqual(result['health_score'], 90)

    def test_info_is_still_counted(self):
        data = basic_workflow()
        data['transitions'].append({'from': 'Open', 'to': 'Open', 'name': 'Refresh'})
        result = WORKFLOW.validate_workflow(data)
        self.assertEqual(result['summary'], {'errors': 0, 'warnings': 0, 'info': 1})
        self.assertEqual(result['health_score'], 97)

    def test_all_severities_and_input_preservation(self):
        data = basic_workflow()
        data['states'].append('Blocked')
        data['transitions'].append({'from': 'Open', 'to': 'Open', 'name': 'Refresh'})
        original = copy.deepcopy(data)
        result = WORKFLOW.validate_workflow(data)
        self.assertEqual(data, original)
        self.assertTrue(all(value > 0 for value in result['summary'].values()))
        self.assert_summary(result)
        self.assertEqual(result['health_score'], 47)

    def test_empty_workflow_still_reports_one_error(self):
        result = WORKFLOW.validate_workflow({})
        self.assertEqual(result['summary'], {'errors': 1, 'warnings': 0, 'info': 0})
        self.assertEqual(result['grade'], 'invalid')
        self.assert_summary(result)

    def test_text_summary_matches_findings(self):
        data = basic_workflow()
        data['transitions'] = []
        result = WORKFLOW.validate_workflow(data)
        text = WORKFLOW.format_text_output(result)
        self.assertIn(f"Errors: {result['summary']['errors']}", text)
        self.assertIn(f"Warnings: {result['summary']['warnings']}", text)
        self.assert_summary(result)

    def test_both_cli_formats(self):
        data = basic_workflow()
        data['transitions'] = []
        expected = WORKFLOW.validate_workflow(data)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'workflow.json'
            source.write_text(json.dumps(data))
            for output_format in ('json', 'text'):
                completed = subprocess.run([sys.executable, str(SCRIPT), str(source),
                                            '--format', output_format], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, '')
                if output_format == 'json':
                    self.assertEqual(json.loads(completed.stdout), expected)
                    self.assert_summary(json.loads(completed.stdout))
                else:
                    self.assertEqual(completed.stdout, WORKFLOW.format_text_output(expected) + '\n')


if __name__ == '__main__':
    unittest.main()

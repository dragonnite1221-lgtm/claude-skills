import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/release-manager/release_planner.py'
SPEC = importlib.util.spec_from_file_location('release_inputs_under_test', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def valid_plan():
    return {'release_name': 'Test', 'version': '1.0.0',
            'features': [{'id': 'ready', 'title': 'Ready feature', 'status': 'ready',
                          'qa_approved': True, 'pm_approved': True}],
            'quality_gates': [{'name': 'Tests', 'required': True, 'status': 'ready'}]}


class ReleasePlanInputTests(unittest.TestCase):
    def test_valid_ready_plan_preserves_all_items(self):
        plan = valid_plan()
        plan['features'].append(dict(plan['features'][0], id='second'))
        planner = MODULE.ReleasePlanner()
        planner.load_release_plan(plan)
        assessment = planner.assess_release_readiness()
        self.assertEqual(assessment['overall_status'], 'ready')
        self.assertEqual(assessment['feature_summary']['total'], 2)
        self.assertEqual(assessment['quality_gate_summary']['total'], 1)

    def test_invalid_feature_cannot_be_dropped(self):
        variants = [{'id': 'bad', 'title': 'Bad', 'status': 'typo'},
                    {'id': 'bad', 'title': 'Bad', 'risk_level': 'urgent'},
                    {'id': 'bad'}, {'title': 'Bad'}, None, 'not an object']
        for invalid in variants:
            for index in [0, 1]:
                with self.subTest(invalid=invalid, index=index):
                    plan = valid_plan()
                    plan['features'].insert(index, invalid)
                    with self.assertRaisesRegex(ValueError, f'feature at index {index}'):
                        MODULE.ReleasePlanner().load_release_plan(plan)

    def test_invalid_quality_gate_cannot_be_dropped(self):
        for invalid in [{'name': 'Required', 'required': True, 'status': 'faled'},
                        {'required': True, 'status': 'failed'}, None, 'not an object']:
            for index in [0, 1]:
                with self.subTest(invalid=invalid, index=index):
                    plan = valid_plan()
                    plan['quality_gates'].insert(index, invalid)
                    with self.assertRaisesRegex(ValueError, f'quality gate at index {index}'):
                        MODULE.ReleasePlanner().load_release_plan(plan)

    def test_existing_valid_blockers_remain_blocked(self):
        for field, status in [('features', 'blocked'), ('quality_gates', 'failed')]:
            with self.subTest(field=field):
                plan = valid_plan()
                plan[field][0]['status'] = status
                planner = MODULE.ReleasePlanner()
                planner.load_release_plan(plan)
                self.assertEqual(planner.assess_release_readiness()['overall_status'], 'blocked')

    def test_default_gates_remain_pending(self):
        planner = MODULE.ReleasePlanner()
        planner.load_release_plan({'features': []})
        assessment = planner.assess_release_readiness()
        self.assertEqual(len(planner.quality_gates), 6)
        self.assertEqual(assessment['overall_status'], 'at_risk')

    def test_dict_input_is_unchanged_and_matches_json_input(self):
        plan = valid_plan()
        original = copy.deepcopy(plan)
        planner = MODULE.ReleasePlanner()
        planner.load_release_plan(plan)
        self.assertEqual(planner.assess_release_readiness()['overall_status'], 'ready')
        self.assertEqual(plan, original)
        from_json = MODULE.ReleasePlanner()
        from_json.load_release_plan(json.dumps(original))
        self.assertEqual(planner.assess_release_readiness(), from_json.assess_release_readiness())

    def test_cli_rejects_bad_entries_without_output_or_overwrite(self):
        for field, invalid in [('features', {'id': 'bad'}),
                               ('quality_gates', {'name': 'Required', 'status': 'typo'})]:
            for output_format in ['json', 'text', 'markdown']:
                with self.subTest(field=field, output_format=output_format):
                    with tempfile.TemporaryDirectory() as temp:
                        root = Path(temp)
                        plan = valid_plan()
                        plan[field].append(invalid)
                        source, output = root / 'plan.json', root / 'report.txt'
                        source.write_text(json.dumps(plan), encoding='utf-8')
                        output.write_text('preserve existing report', encoding='utf-8')
                        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '-i', str(source),
                                                 '-f', output_format, '-o', str(output)],
                                                text=True, capture_output=True)
                        self.assertEqual(result.returncode, 1)
                        self.assertEqual(result.stdout, '')
                        self.assertIn('Error loading release plan:', result.stderr)
                        self.assertEqual(output.read_text(encoding='utf-8'), 'preserve existing report')


if __name__ == '__main__':
    unittest.main()

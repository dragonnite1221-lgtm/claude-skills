"""Regression coverage for effective OpenAPI Path Item parameters."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/api-design-reviewer/scripts/breaking_change_detector.py'
SPEC = importlib.util.spec_from_file_location('shared_parameter_detector', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def parameter(required=False, kind='string', location='query'):
    return {'name': 'token', 'in': location, 'required': required, 'schema': {'type': kind}}


def document(shared=None, operations=None):
    item = {'get': {'responses': {'200': {'description': 'OK'}}}}
    if shared is not None:
        item['parameters'] = shared
    if operations:
        item.update(operations)
    return {'openapi': '3.0.3', 'info': {'title': 'API', 'version': '1'}, 'paths': {'/items': item}}


class SharedParameterTests(unittest.TestCase):
    def compare(self, old, new):
        before = copy.deepcopy((old, new))
        detector = MODULE.BreakingChangeDetector()
        report = detector.compare_specs(old, new)
        self.assertEqual((old, new), before)
        self.assertEqual(json.loads(detector.generate_json_report())['hasBreakingChanges'], report.has_breaking_changes())
        return report

    def test_shared_breaking_changes(self):
        pairs = [(None, [parameter(True)]), ([parameter()], [parameter(True)]),
                 ([parameter()], [parameter(kind='integer')]), ([parameter()], [])]
        for old, new in pairs:
            with self.subTest(old=old, new=new):
                report = self.compare(document(old), document(new))
                self.assertTrue(report.has_breaking_changes())
                self.assertEqual(len(report.changes), 1)
                self.assertTrue(report.changes[0].path.startswith('/paths/items/get/parameters'))

    def test_operation_override_and_identity(self):
        override = {'get': {'parameters': [parameter()], 'responses': {}}}
        self.assertFalse(self.compare(document([parameter()], override), document([parameter(True)], override)).has_breaking_changes())
        header_override = {'get': {'parameters': [parameter(location='header')], 'responses': {}}}
        self.assertTrue(self.compare(document([parameter()], header_override), document([parameter(True)], header_override)).has_breaking_changes())
        self.assertTrue(self.compare(document([parameter()], override), document([parameter(True)], {'get': {'responses': {}}})).has_breaking_changes())

    def test_moving_declarations_preserves_effective_contract(self):
        shared = document([parameter(True)])
        local = document(None, {'get': {'parameters': [parameter(True)], 'responses': {'200': {'description': 'OK'}}}})
        self.assertEqual(self.compare(shared, local).changes, [])
        self.assertEqual(self.compare(local, shared).changes, [])
        self.assertFalse(self.compare(document([parameter(True)]), document([parameter()])).has_breaking_changes())

    def test_each_operation_inherits_independently(self):
        ops = {'post': {'responses': {}}, 'delete': {'parameters': [parameter()], 'responses': {}}}
        report = self.compare(document([parameter()], ops), document([parameter(True)], ops))
        self.assertEqual(report.summary['breaking_changes'], 2)
        self.assertEqual({c.path.split('/')[3] for c in report.changes}, {'get', 'post'})

    def test_cli_gate_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            old, new = Path(directory) / 'old.json', Path(directory) / 'new.json'
            old.write_text(json.dumps(document([parameter()])))
            new.write_text(json.dumps(document([parameter(True)])))
            command = [sys.executable, str(SCRIPT), str(old), str(new), '--format', 'json']
            for gate, code in [(False, 0), (True, 1)]:
                result = subprocess.run(command + (['--exit-on-breaking'] if gate else []), capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertTrue(json.loads(result.stdout)['hasBreakingChanges'])


if __name__ == '__main__':
    unittest.main()

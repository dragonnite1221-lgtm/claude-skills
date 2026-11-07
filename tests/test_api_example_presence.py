"""Explicit falsy JSON examples count as documentation, not missing values."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'engineering/api-design-reviewer/scripts/api_scorecard.py'
SPEC = importlib.util.spec_from_file_location('scorecard_example_presence', PATH)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
VALUES = [0, False, '', [], {}, None, 1, True, 'example']


class ExamplePresenceTests(unittest.TestCase):
    def test_media_examples(self):
        engine = MOD.APIScoringEngine()
        for value in VALUES:
            with self.subTest(value=value):
                self.assertTrue(engine._has_examples({'application/json': {'example': value}}))
        self.assertFalse(engine._has_examples({'application/json': {}}))
        self.assertFalse(engine._has_examples({'application/json': {'examples': {}}}))
        self.assertTrue(engine._has_examples({'application/json': {'examples': {'zero': {'value': 0}}}}))

    def test_schema_and_property_examples(self):
        engine = MOD.APIScoringEngine()
        for value in VALUES:
            for schema in [{'example': value}, {'properties': {'value': {'example': value}}}]:
                with self.subTest(value=value, schema=schema):
                    self.assertTrue(engine._schema_has_examples(schema))
        self.assertFalse(engine._schema_has_examples({'properties': {'value': {}}}))

    def test_documentation_checks(self):
        engine = MOD.APIScoringEngine()
        for value in VALUES:
            for schema in [{'description': 'Value', 'example': value},
                           {'description': 'Value', 'properties': {'value': {'example': value}}}]:
                engine.spec = {'components': {'schemas': {'Value': schema}}}
                with self.subTest(schema=schema):
                    self.assertEqual(engine._check_schema_documentation(), 100)
            for param in [{'name': 'value', 'in': 'query', 'example': value},
                          {'name': 'value', 'in': 'query', 'schema': {'example': value}}]:
                engine.spec = {'paths': {'/values': {'get': {'parameters': [param]}}}}
                with self.subTest(param=param):
                    self.assertEqual(engine._check_parameter_documentation(), 100)

    def test_complete_score_matches_truthy_example(self):
        engine = MOD.APIScoringEngine()
        baseline = None
        for value in VALUES:
            spec = {'openapi': '3.0.0', 'info': {'title': 'Example', 'version': '1'},
                    'paths': {'/values': {'get': {'parameters': [{'name': 'value', 'in': 'query', 'example': value}],
                              'responses': {'200': {'description': 'Value', 'content': {'application/json': {'example': value}}}}}}},
                    'components': {'schemas': {'Value': {'description': 'Value', 'example': value}}}}
            saved = copy.deepcopy(spec)
            engine.score_api(spec)
            report = json.loads(engine.generate_json_report())
            if baseline is None:
                baseline = report
            with self.subTest(value=value):
                self.assertEqual(report, baseline)
                self.assertEqual(spec, saved)
            self.assertEqual(engine._check_example_coverage(), 100)

    def test_absent_examples_stay_absent(self):
        engine = MOD.APIScoringEngine()
        engine.spec = {'paths': {'/values': {'get': {'responses': {'200': {'content': {'application/json': {}}}},
                       'parameters': [{'name': 'value', 'in': 'query'}]}}},
                       'components': {'schemas': {'Value': {'description': 'Value'}}}}
        self.assertEqual(engine._check_example_coverage(), 0)
        self.assertEqual(engine._check_schema_documentation(), 0)
        self.assertEqual(engine._check_parameter_documentation(), 0)


if __name__ == '__main__':
    unittest.main()

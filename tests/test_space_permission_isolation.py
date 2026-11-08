"""Generated permission suggestions must not share mutable template state."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-management/confluence-expert/scripts/space_structure_generator.py'
SPEC = importlib.util.spec_from_file_location('space_permission_isolation', SCRIPT)
SPACE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SPACE)


class PermissionIsolationTests(unittest.TestCase):
    def test_each_team_gets_independent_mapping_and_lists(self):
        for kind, template in SPACE.PERMISSION_TEMPLATES.items():
            with self.subTest(kind=kind):
                result = SPACE.generate_space_structure({'type': kind})
                self.assertEqual(result['permissions'], template)
                self.assertIsNot(result['permissions'], template)
                for key in template:
                    self.assertIsNot(result['permissions'][key], template[key])

    def test_mutating_lists_does_not_change_templates_or_later_results(self):
        for kind, template in SPACE.PERMISSION_TEMPLATES.items():
            with self.subTest(kind=kind):
                expected = copy.deepcopy(template)
                first = SPACE.generate_space_structure({'name': 'Alpha', 'type': kind})
                for values in first['permissions'].values():
                    values.clear()
                    values.append('synthetic change')
                second = SPACE.generate_space_structure({'name': 'Beta', 'type': kind})
                self.assertEqual(template, expected)
                self.assertEqual(second['permissions'], expected)

    def test_mutating_mapping_does_not_change_later_results(self):
        first = SPACE.generate_space_structure({'type': 'engineering'})
        expected = copy.deepcopy(SPACE.PERMISSION_TEMPLATES['engineering'])
        first['permissions'].pop('restrictions')
        first['permissions']['admins'] = ['synthetic admin']
        first['permissions']['custom'] = ['synthetic group']
        self.assertEqual(SPACE.generate_space_structure({'type': 'engineering'})['permissions'], expected)

    def test_existing_results_do_not_share_lists(self):
        first = SPACE.generate_space_structure({'type': 'product'})
        second = SPACE.generate_space_structure({'type': 'product'})
        expected = copy.deepcopy(second['permissions'])
        first['permissions']['viewers'].append('synthetic viewer')
        self.assertEqual(second['permissions'], expected)

    def test_default_unknown_and_case_normalization(self):
        for data, kind in [({}, 'project'), ({'type': 'unknown'}, 'project'),
                           ({'type': 'ENGINEERING'}, 'engineering')]:
            with self.subTest(data=data):
                result = SPACE.generate_space_structure(data)
                self.assertEqual(result['team_type'], kind)
                self.assertEqual(result['permissions'], SPACE.PERMISSION_TEMPLATES[kind])
                self.assertIsNot(result['permissions'], SPACE.PERMISSION_TEMPLATES[kind])

    def test_input_and_page_templates_are_preserved(self):
        data = {'name': 'Example Team', 'type': 'engineering', 'projects': ['One', {'name': 'Two'}]}
        original = copy.deepcopy(data)
        template = copy.deepcopy(SPACE.BASE_SECTIONS)
        result = SPACE.generate_space_structure(data)
        result['page_tree'][0]['labels'].append('synthetic label')
        self.assertEqual(data, original)
        self.assertEqual(SPACE.BASE_SECTIONS, template)
        self.assertEqual(result['total_pages'], SPACE._count_pages(result['page_tree']))

    def test_json_and_text_cli(self):
        data = {'name': 'Example Team', 'type': 'marketing', 'projects': ['Campaign']}
        expected = SPACE.generate_space_structure(data)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'team.json'
            source.write_text(json.dumps(data))
            for output_format in ('json', 'text'):
                completed = subprocess.run([sys.executable, str(SCRIPT), str(source),
                                            '--format', output_format], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, '')
                if output_format == 'json':
                    self.assertEqual(json.loads(completed.stdout), expected)
                else:
                    self.assertEqual(completed.stdout, SPACE.format_text_output(expected) + '\n')


if __name__ == '__main__':
    unittest.main()

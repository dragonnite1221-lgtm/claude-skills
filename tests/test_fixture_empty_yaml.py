import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering-team/tdd-guide/scripts/fixture_generator.py'
spec = importlib.util.spec_from_file_location('fixture_empty', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EmptyYamlTests(unittest.TestCase):
    def setUp(self):
        self.generator = module.FixtureGenerator()

    def test_root_collections(self):
        for value, expected in [({}, '{}'), ([], '[]')]:
            with self.subTest(value=value):
                self.assertEqual(self.generator.generate_fixture_file('sample', value, 'yaml'), expected)

    def test_nested_collections(self):
        self.assertEqual(self.generator.generate_fixture_file('sample', {'mapping': {}, 'items': []}, 'yaml'),
                         'mapping:\n  {}\nitems:\n  []')

    def test_list_mapping(self):
        self.assertEqual(self.generator.generate_fixture_file('sample', [{}], 'yaml'), '-\n  {}')
        self.assertEqual(self.generator.generate_fixture_file('sample', {'outer': {'inner': []}}, 'yaml'),
                         'outer:\n  inner:\n    []')

    def test_nonempty_controls(self):
        self.assertEqual(self.generator.generate_fixture_file('sample', {'name': 'value', 'count': 2}, 'yaml'),
                         'name: value\ncount: 2')
        self.assertEqual(self.generator.generate_fixture_file('sample', [1, 2], 'yaml'), '- 1\n- 2')
        self.assertEqual(self.generator.generate_fixture_file('sample', {}, 'json'), '{}')


if __name__ == '__main__':
    unittest.main()


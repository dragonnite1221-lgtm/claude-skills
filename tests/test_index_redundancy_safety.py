"""Conservative index-drop recommendations preserve modeled semantics."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'engineering/database-designer/index_optimizer.py'
SPEC = importlib.util.spec_from_file_location('index_redundancy_optimizer', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class IndexRedundancySafetyTests(unittest.TestCase):
    def analyze(self, indexes):
        optimizer = MODULE.IndexOptimizer()
        optimizer.load_schema({'tables': {'items': {
            'columns': {name: {'type': 'INT'} for name in ['a', 'b', 'c']},
            'indexes': indexes,
        }}})
        optimizer.load_query_patterns({'queries': []})
        return optimizer.generate_analysis_report()

    def index(self, name, columns, **kwargs):
        return dict(name=name, columns=columns, **kwargs)

    def test_unique_and_reversed_keys_are_not_dropped(self):
        pairs = [
            [self.index('unique_a', ['a'], unique=True), self.index('plain_a', ['a'])],
            [self.index('unique_a', ['a'], unique=True), self.index('long_ab', ['a', 'b'])],
            [self.index('ab', ['a', 'b']), self.index('ba', ['b', 'a'])],
        ]
        for pair in pairs:
            for indexes in [pair, list(reversed(pair))]:
                with self.subTest(indexes=indexes):
                    self.assertEqual(self.analyze(indexes)['sql_statements']['drop_redundant'], [])

    def test_duplicate_identity_includes_type_predicate_and_include(self):
        for change in [dict(type='hash'), dict(partial_condition='a > 0'), dict(include_columns=['b'])]:
            with self.subTest(change=change):
                indexes = [self.index('plain', ['a']), self.index('different', ['a'], **change)]
                self.assertEqual(self.analyze(indexes)['sql_statements']['drop_redundant'], [])

    def test_exact_duplicates_keep_one_survivor(self):
        for kwargs in [{}, dict(unique=True), dict(include_columns=['b']), dict(type='hash')]:
            with self.subTest(kwargs=kwargs):
                indexes = [self.index(name, ['a'], **kwargs) for name in ['first', 'second', 'third']]
                report = self.analyze(indexes)
                self.assertEqual(report['sql_statements']['drop_redundant'],
                                 ['DROP INDEX second;', 'DROP INDEX third;'])
                self.assertEqual([r['issue_type'] for r in report['redundancy_analysis']],
                                 ['DUPLICATE', 'DUPLICATE'])

    def test_strict_prefix_requires_compatible_semantics(self):
        short = self.index('short', ['a'], include_columns=['c'])
        for longer, expected in [
            (self.index('long', ['a', 'b'], include_columns=['c']), ['DROP INDEX short;']),
            (self.index('long', ['a', 'c']), ['DROP INDEX short;']),
            (self.index('long', ['a', 'b']), []),
            (self.index('long', ['a', 'b'], type='hash', include_columns=['c']), []),
            (self.index('long', ['a', 'b'], partial_condition='a > 0', include_columns=['c']), []),
        ]:
            for indexes in [[short, longer], [longer, short]]:
                with self.subTest(indexes=indexes):
                    self.assertEqual(self.analyze(indexes)['sql_statements']['drop_redundant'], expected)

    def test_cli_never_emits_both_duplicate_drop_targets(self):
        schema = {'tables': {'items': {'columns': {'a': {'type': 'INT'}}, 'indexes': [
            self.index('first', ['a']), self.index('second', ['a'])]}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'schema.json').write_text(json.dumps(schema))
            (root / 'queries.json').write_text('{"queries": []}')
            run = subprocess.run([sys.executable, str(PATH), '--schema', str(root / 'schema.json'),
                                  '--queries', str(root / 'queries.json'), '--format', 'json'],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['sql_statements']['drop_redundant'],
                             ['DROP INDEX second;'])


if __name__ == '__main__':
    unittest.main()

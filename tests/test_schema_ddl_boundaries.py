"""Regression coverage for complete CREATE TABLE body extraction."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/database-designer/schema_analyzer.py'
spec = importlib.util.spec_from_file_location('schema_ddl_boundaries', SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class SchemaDdlBoundariesTests(unittest.TestCase):
    def test_parameterized_types_preserve_following_columns_and_constraints(self):
        analyzer = module.SchemaAnalyzer()
        analyzer.parse_sql_ddl('''CREATE TABLE users (
            id INTEGER PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE,
            amount DECIMAL(10,2), age INTEGER, UNIQUE (age));
            CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
            CREATE INDEX idx_users_age ON users(age);''')
        users = analyzer.tables['users']
        self.assertEqual([c.name for c in users.columns], ['id', 'email', 'amount', 'age'])
        self.assertEqual(users.columns[1].data_type, 'VARCHAR(255)')
        self.assertFalse(users.columns[1].nullable)
        self.assertTrue(users.columns[1].unique)
        self.assertEqual(users.columns[2].data_type, 'DECIMAL(10,2)')
        self.assertEqual(users.unique_constraints, [['age']])
        self.assertEqual(users.indexes[0].columns, ['age'])
        self.assertEqual([c.name for c in analyzer.tables['teams'].columns], ['id', 'name'])

    def test_nested_checks_and_quoted_tokens_do_not_end_table_or_split_columns(self):
        for literal in ["')'", "'('", "'a,b'", "'it''s )('", '"a,b)("']:
            with self.subTest(literal=literal):
                analyzer = module.SchemaAnalyzer()
                analyzer.parse_sql_ddl(
                    f'CREATE TABLE items (id INTEGER, label TEXT DEFAULT {literal}, '
                    'amount INTEGER CHECK ((amount + 1) > 0), tail INTEGER, PRIMARY KEY (id));'
                )
                self.assertEqual([c.name for c in analyzer.tables['items'].columns],
                                 ['id', 'label', 'amount', 'tail'])
                self.assertEqual(analyzer.tables['items'].primary_key, ['id'])

    def test_create_table_text_inside_body_is_not_a_new_table(self):
        analyzer = module.SchemaAnalyzer()
        analyzer.parse_sql_ddl("CREATE TABLE items (label TEXT DEFAULT 'CREATE TABLE fake (x INT)', tail INT);")
        self.assertEqual(list(analyzer.tables), ['items'])
        self.assertEqual([c.name for c in analyzer.tables['items'].columns], ['label', 'tail'])

    def test_unclosed_table_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unclosed table definition: items'):
            module.SchemaAnalyzer().parse_sql_ddl('CREATE TABLE items (id INTEGER, label VARCHAR(20)')

    def test_cli_reports_complete_schema_and_rejects_unclosed_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'schema.sql'
            path.write_text('CREATE TABLE users (id INTEGER, label VARCHAR(20), age INTEGER);')
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(path),
                                     '--output-format', 'json', '--generate-erd'],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['schema_overview']['total_columns'], 3)
            self.assertIn('INTEGER age', report['mermaid_erd'])
            path.write_text('CREATE TABLE users (label VARCHAR(20)')
            failed = subprocess.run([sys.executable, str(SCRIPT), '--input', str(path)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(failed.returncode, 1)
            self.assertIn('Unclosed table definition', failed.stderr)
            self.assertEqual(failed.stdout, '')


if __name__ == '__main__':
    unittest.main()

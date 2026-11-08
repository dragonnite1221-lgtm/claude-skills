"""Incomplete date metadata must not prevent a content audit report."""
import copy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-management/confluence-expert/scripts/content_audit_analyzer.py'
SPEC = importlib.util.spec_from_file_location('content_audit_null_dates', SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def page(date):
    return {'title': 'Synthetic page', 'last_modified': date, 'author': 'Test',
            'view_count': 10, 'labels': ['test'], 'word_count': 400}


class NullDateTests(unittest.TestCase):
    def test_null_date_is_unparseable(self):
        self.assertIsNone(AUDIT._parse_date(None))

    def test_other_non_string_dates_are_unparseable(self):
        for value in (False, 0, 1.5, [], {}, ['2026-01-01']):
            with self.subTest(value=value):
                self.assertIsNone(AUDIT._parse_date(value))

    def test_valid_formats_are_preserved(self):
        values = ['2026-01-15', '2026-01-15T12:30:45', '2026-01-15T12:30:45Z',
                  '2026-01-15T12:30:45.123', '2026-01-15T12:30:45.123Z',
                  '15/01/2026', '01/15/2026']
        for value in values:
            with self.subTest(value=value):
                parsed = AUDIT._parse_date(value)
                self.assertEqual(parsed.date(), datetime(2026, 1, 15).date())
        self.assertEqual(AUDIT._parse_date(values[1]).hour, 12)
        self.assertEqual(AUDIT._parse_date(values[3]).microsecond, 123000)

    def test_invalid_strings_still_return_none(self):
        for value in ('', 'not a date', '2026-02-30', '2026-99-99'):
            self.assertIsNone(AUDIT._parse_date(value))

    def test_null_is_equivalent_to_missing_date(self):
        null = {'pages': [page(None)]}
        missing = copy.deepcopy(null)
        del missing['pages'][0]['last_modified']
        original = copy.deepcopy(null)
        result = AUDIT.analyze_content_health(null)
        self.assertEqual(result, AUDIT.analyze_content_health(missing))
        self.assertEqual(null, original)
        self.assertEqual(result['health_score'], 90)
        self.assertEqual(result['dimensions']['completeness']['incomplete_count'], 1)
        self.assertEqual(result['dimensions']['completeness']['incomplete_pages'][0]['missing_fields'], ['last_modified'])

    def test_mixed_inventory_continues_valid_date_checks(self):
        result = AUDIT.check_stale_pages([page(None), page('2026-01-01'),
                                         page('2026-07-01'), page('2026-10-01')],
                                        datetime(2026, 11, 8))
        self.assertEqual(result['outdated_count'], 1)
        self.assertEqual(result['stale_count'], 1)
        self.assertEqual(result['fresh_count'], 2)

    def test_null_metadata_generates_action(self):
        result = AUDIT.analyze_content_health({'pages': [page(None)]})
        self.assertTrue(any(item['category'] == 'completeness' for item in result['action_items']))
        self.assertIn('Incomplete: 1', AUDIT.format_text_output(result))

    def test_json_and_text_cli_complete(self):
        data = {'pages': [page(None), page('2000-01-01')]}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'pages.json'
            source.write_text(json.dumps(data))
            for output_format in ('json', 'text'):
                completed = subprocess.run([sys.executable, str(SCRIPT), str(source),
                                            '--format', output_format], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, '')
                if output_format == 'json':
                    result = json.loads(completed.stdout)
                    self.assertEqual(result['dimensions']['completeness']['incomplete_count'], 1)
                    self.assertEqual(result['dimensions']['freshness']['outdated_count'], 1)
                else:
                    self.assertIn('Total Pages Analyzed: 2', completed.stdout)
                    self.assertIn('Incomplete: 1', completed.stdout)


if __name__ == '__main__':
    unittest.main()

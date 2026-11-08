"""Blocked-status alternatives must both respect a requested project scope."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-management/jira-expert/scripts/jql_query_builder.py'
SPEC = importlib.util.spec_from_file_location('jql_blocked_project_scope', SCRIPT)
JQL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JQL)


def matches(query, project, status):
    """Evaluate only equality/AND/OR in these fixed synthetic queries."""
    values = {'project': project, 'status': status}
    expression = re.sub(r'\b(project|status) = (\w+)',
                        lambda m: str(values[m[1]] == m[2]), query)
    expression = expression.replace(' AND ', ' and ').replace(' OR ', ' or ')

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BoolOp):
            values = [evaluate(value) for value in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        raise AssertionError('Unexpected syntax in controlled test expression')

    return evaluate(ast.parse(expression, mode='eval').body)


class BlockedProjectScopeTests(unittest.TestCase):
    def test_project_applies_to_both_status_alternatives(self):
        result = JQL.build_jql_from_description('blocked issues in ABC')
        self.assertEqual(result['jql'], 'project = ABC AND (status = Blocked OR status = Impediment)')
        for project in ('ABC', 'OTHER'):
            for status in ('Blocked', 'Impediment', 'Done', 'Open'):
                with self.subTest(project=project, status=status):
                    self.assertEqual(matches(result['jql'], project, status),
                                     project == 'ABC' and status in ('Blocked', 'Impediment'))

    def test_all_blocked_aliases_and_project_keys(self):
        for phrase in JQL.PATTERN_LIBRARY['blocked_issues']['phrases']:
            for project in ('ABC', 'PROJ', 'OPS'):
                with self.subTest(phrase=phrase, project=project):
                    result = JQL.build_jql_from_description(f'{phrase} in {project}')
                    self.assertTrue(matches(result['jql'], project, 'Impediment'))
                    self.assertFalse(matches(result['jql'], 'OTHER', 'Impediment'))
                    self.assertTrue(JQL.validate_jql_syntax(result['jql'])['valid'])

    def test_unscoped_blocked_query_keeps_both_statuses(self):
        query = JQL.build_jql_from_description('blocked issues')['jql']
        for project in ('ABC', 'OTHER'):
            self.assertTrue(matches(query, project, 'Blocked'))
            self.assertTrue(matches(query, project, 'Impediment'))
            self.assertFalse(matches(query, project, 'Done'))

    def test_result_metadata_and_library_are_preserved(self):
        library = copy.deepcopy(JQL.PATTERN_LIBRARY)
        result = JQL.build_jql_from_description('blocked issues in ABC')
        self.assertEqual(result['pattern_name'], 'blocked_issues')
        self.assertEqual(result['description'], 'Issues in blocked or impediment status')
        self.assertEqual(result['match_type'], 'exact_pattern')
        self.assertEqual(JQL.PATTERN_LIBRARY, library)

    def test_other_queries_are_unchanged(self):
        cases = {'overdue in ABC': 'project = ABC AND duedate < now() AND status != Done',
                 'recently created in ABC': 'project = ABC AND created >= -7d ORDER BY created DESC',
                 'my bugs': 'assignee = currentUser() AND type = Bug AND status != Done'}
        for description, query in cases.items():
            self.assertEqual(JQL.build_jql_from_description(description)['jql'], query)

    def test_pattern_listing_contains_grouped_expression(self):
        patterns = json.loads(JQL.format_patterns_output('json'))
        self.assertEqual(patterns['blocked_issues']['jql'], '(status = Blocked OR status = Impediment)')
        self.assertIn('(status = Blocked OR status = Impediment)', JQL.format_patterns_output('text'))

    def test_json_and_text_cli(self):
        for output_format in ('json', 'text'):
            completed = subprocess.run([sys.executable, str(SCRIPT), 'blocked issues in ABC',
                                        '--format', output_format], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stderr, '')
            query = 'project = ABC AND (status = Blocked OR status = Impediment)'
            if output_format == 'json':
                result = json.loads(completed.stdout)
                self.assertEqual(result['jql'], query)
                self.assertTrue(result['validation']['valid'])
            else:
                self.assertIn(query, completed.stdout)
                self.assertIn('Valid: Yes', completed.stdout)


if __name__ == '__main__':
    unittest.main()

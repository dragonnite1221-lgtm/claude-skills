"""Recognize the canonical Jira project administration permission name."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'project-management/atlassian-admin/scripts/permission_audit_tool.py'
SPEC = importlib.util.spec_from_file_location('permission_project_admin_alias', SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def scheme(permissions, holder='group'):
    return {'name': 'Synthetic scheme', 'grants': [
        {'permission': permission, holder: 'synthetic-holder'} for permission in permissions]}


class ProjectAdminAliasTests(unittest.TestCase):
    def test_canonical_group_admin_is_recognized(self):
        for permission in ('ADMINISTER_PROJECTS', 'administer_projects', 'Administer_Projects'):
            with self.subTest(permission=permission):
                result = AUDIT.audit_permissions(scheme([permission]))
                self.assertFalse(any(f['rule'] == 'no_admin_defined' for f in result['findings']))
                self.assertEqual(result['risk_score'], 0)

    def test_canonical_direct_admin_is_high_severity(self):
        result = AUDIT.audit_permissions(scheme(['ADMINISTER_PROJECTS'], 'user'))
        self.assertEqual([(f['rule'], f['severity']) for f in result['findings']],
                         [('direct_user_permission', 'high')])
        self.assertEqual(result['risk_score'], 15)

    def test_legacy_singular_name_remains_supported(self):
        result = AUDIT.audit_permissions(scheme(['administer_project'], 'user'))
        self.assertEqual(result['summary']['high'], 1)
        self.assertEqual(result['summary']['medium'], 0)
        self.assertEqual(result['risk_score'], 15)

    def test_canonical_admin_counts_toward_sensitive_threshold(self):
        findings = AUDIT.check_over_permissioned_groups([
            scheme(['ADMINISTER_PROJECTS', 'delete_issues', 'bulk_change'])])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['rule'], 'over_permissioned_group')
        self.assertIn('3 sensitive permissions', findings[0]['message'])

    def test_aliases_do_not_double_count_sensitive_permission(self):
        findings = AUDIT.check_over_permissioned_groups([
            scheme(['ADMINISTER_PROJECTS', 'administer_project', 'delete_issues'])])
        self.assertEqual(findings, [])

    def test_canonical_admin_is_seen_by_compliance_check(self):
        data = scheme(['ADMINISTER_PROJECTS'])
        data['grants'].append({'permission': 'browse_projects', 'group': 'other-group'})
        findings = AUDIT.check_compliance_gaps([data])
        self.assertEqual([f['rule'] for f in findings], ['separation_of_duties'])

    def test_unrelated_sensitive_rules_and_input_preserved(self):
        data = scheme(['administer_project'])
        data['grants'].append({'permission': 'delete_issues', 'group': 'jira-users'})
        original = copy.deepcopy(data)
        result = AUDIT.audit_permissions(data)
        self.assertEqual(data, original)
        self.assertEqual([(f['rule'], f['severity']) for f in result['findings']],
                         [('unrestricted_delete', 'critical')])

    def test_both_cli_formats(self):
        data = scheme(['ADMINISTER_PROJECTS'], 'user')
        expected = AUDIT.audit_permissions(data)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'permissions.json'
            source.write_text(json.dumps(data))
            for output_format in ('json', 'text'):
                completed = subprocess.run([sys.executable, str(SCRIPT), str(source),
                                            '--format', output_format], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, '')
                if output_format == 'json':
                    self.assertEqual(json.loads(completed.stdout), expected)
                else:
                    self.assertEqual(completed.stdout, AUDIT.format_text_output(expected) + '\n')


if __name__ == '__main__':
    unittest.main()

"""Lockfile package identity must retain scopes and explicit package names."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/dependency-auditor/scripts/dep_scanner.py'
SPEC = importlib.util.spec_from_file_location('npm_identity_scanner', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class LockIdentityTests(unittest.TestCase):
    def parse(self, packages):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'package-lock.json'
            file.write_text(json.dumps({'lockfileVersion': 3, 'packages': packages}))
            return MODULE.DependencyScanner()._parse_package_lock(file)

    def test_scoped_and_nested_names(self):
        paths = ['node_modules/@scope/pkg', 'node_modules/outer/node_modules/@scope/pkg',
                 'node_modules/@outer/parent/node_modules/@inner/child', 'node_modules/plain']
        parsed = self.parse({p: {'version': '1.2.3'} for p in paths})
        self.assertEqual([p.name for p in parsed], ['@scope/pkg', '@scope/pkg', '@inner/child', 'plain'])
        self.assertTrue(all(p.ecosystem == 'npm' and not p.direct for p in parsed))

    def test_explicit_alias_and_workspace_names(self):
        parsed = self.parse({'node_modules/alias': {'name': '@actual/pkg', 'version': '2.0.0'},
                             'packages/local': {'name': '@workspace/local', 'version': '3.0.0'}})
        self.assertEqual([p.name for p in parsed], ['@actual/pkg', '@workspace/local'])
        self.assertEqual([p.version for p in parsed], ['2.0.0', '3.0.0'])

    def test_root_skipped_and_description_preserved(self):
        parsed = self.parse({'': {'name': 'root', 'version': '1'},
                            'node_modules/plain': {'version': '1.0.0', 'description': 'description'}})
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].name, 'plain')
        self.assertEqual(parsed[0].description, 'description')

    def test_scoped_name_does_not_inherit_unscoped_advisory(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'package-lock.json'
            file.write_text(json.dumps({'packages': {'node_modules/@custom/lodash': {'version': '4.17.20'}}}))
            scanner = MODULE.DependencyScanner()
            report = scanner.scan_project(directory)
            self.assertEqual(report['dependencies'][0].name, '@custom/lodash')
            self.assertEqual(report['vulnerabilities_found'], 0)
            result = subprocess.run([sys.executable, str(SCRIPT), directory, '--format', 'json', '--fail-on-high'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['high_severity_count'], 0)


if __name__ == '__main__':
    unittest.main()

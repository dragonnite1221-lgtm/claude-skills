"""Declared licenses must match whole supported identifiers, not substrings."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/dependency-auditor/scripts/license_checker.py'
spec = importlib.util.spec_from_file_location('license_alias_checker', SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class LicenseAliasTests(unittest.TestCase):
    def setUp(self):
        self.checker = module.LicenseChecker()

    def test_canonical_ids_ignore_case_without_family_collisions(self):
        for name, expected in self.checker.license_database.items():
            for value in (name, name.lower(), name.swapcase(), '  ' + name.lower() + '\t'):
                with self.subTest(value=value):
                    self.assertIs(self.checker._resolve_license_info(value), expected)

    def test_supported_aliases_remain_available(self):
        aliases = {'apache': 'Apache-2.0', 'apache 2.0': 'Apache-2.0',
                   'bsd': 'BSD-3-Clause', 'unlicense': 'MIT',
                   'public domain': 'MIT', 'commercial': 'PROPRIETARY'}
        for alias, name in aliases.items():
            with self.subTest(alias=alias):
                self.assertIs(self.checker._resolve_license_info(alias.upper()),
                              self.checker.license_database[name])

    def test_unsupported_declarations_are_not_substring_matches(self):
        values = ['MIT AND GPL-3.0', 'MIT OR GPL-3.0', '(MIT)',
                  'GPL-3.0 WITH Classpath-exception-2.0', 'LicenseRef-MIT-custom',
                  'MIT-custom', 'GPL-3.0-only', 'MIT License', 'permit',
                  'disclaimer', 'Apache-2.0-extra', 'BSD-3-Clause-extra', '']
        for value in values:
            with self.subTest(value=value):
                self.assertIsNone(self.checker._resolve_license_info(value))

    def test_unknown_declaration_uses_existing_unknown_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            dep = self.checker._analyze_dependency_license(
                {'name': 'test', 'license': 'MIT AND GPL-3.0', 'ecosystem': 'npm'},
                Path(directory))
            self.assertEqual(dep.license_declared, 'MIT AND GPL-3.0')
            self.assertIs(dep.license_detected, self.checker.license_database['UNKNOWN'])
            self.assertEqual(dep.confidence, 0)

    def test_strict_cli_does_not_pass_unresolved_compound(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / 'deps.json'
            inventory.write_text(json.dumps({'dependencies': [
                {'name': 'test', 'license': 'MIT AND GPL-3.0'}]}))
            result = subprocess.run([sys.executable, str(SCRIPT), str(root),
                                     '--inventory', str(inventory), '--format', 'json',
                                     '--policy', 'strict'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['license_summary']['unknown_licenses'], 1)
            self.assertEqual(report['dependencies'][0]['confidence'], 0)


if __name__ == '__main__':
    unittest.main()

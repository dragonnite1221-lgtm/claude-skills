"""SemVer precedence regressions; no package registry or install is contacted."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'engineering/dependency-auditor/scripts/upgrade_planner.py'
spec = importlib.util.spec_from_file_location('upgrade_semver_target', SOURCE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class UpgradeSemverTests(unittest.TestCase):
    def setUp(self):
        self.planner = module.UpgradePlanner()

    def test_build_metadata_does_not_change_release_numbers(self):
        for value in ['1.2.3+4', '1.2.3+build.8', '1.2.3-rc.2+sha.123']:
            with self.subTest(value=value):
                parsed = self.planner._parse_version(value)
                self.assertEqual((parsed.major, parsed.minor, parsed.patch), (1, 2, 3))
                self.assertEqual(str(parsed), value)
        self.assertEqual(self.planner._compare_versions(
            self.planner._parse_version('1.2.3+4'), self.planner._parse_version('1.2.3+999')), 0)

    def test_semver_prerelease_identifier_precedence(self):
        order = ['1.0.0-alpha', '1.0.0-alpha.1', '1.0.0-alpha.beta',
                 '1.0.0-beta', '1.0.0-beta.2', '1.0.0-beta.11', '1.0.0-rc.1', '1.0.0']
        for first, second in zip(order, order[1:]):
            with self.subTest(first=first, second=second):
                a, b = self.planner._parse_version(first), self.planner._parse_version(second)
                self.assertEqual(self.planner._compare_versions(a, b), -1)
                self.assertEqual(self.planner._compare_versions(b, a), 1)
        self.assertTrue(self.planner._is_version_greater('1.2.3-rc.10', '1.2.3-rc.2'))
        self.assertFalse(self.planner._is_version_greater('1.2.3+5', '1.2.3+4'))

    def test_advisory_comparison_accepts_prerelease_and_build(self):
        for current in ['4.17.20+4', '4.17.21-rc.2+build.1']:
            with self.subTest(current=current):
                result = self.planner._analyze_dependency_upgrade(
                    {'name': 'lodash', 'version': current, 'ecosystem': 'npm', 'direct': True})
                self.assertIsNotNone(result)
                self.assertEqual(result.latest_version, '4.17.21')
                self.assertTrue(result.security_updates)
        self.assertIsNone(self.planner._analyze_dependency_upgrade(
            {'name': 'lodash', 'version': '4.17.21+9', 'ecosystem': 'npm'}))

    def test_inventory_reports_generated_without_version_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'inventory.json'
            path.write_text(json.dumps({'dependencies': [
                {'name': 'lodash', 'version': '4.17.20+4', 'ecosystem': 'npm'}]}))
            report = self.planner.analyze_upgrades(str(path))
        self.assertEqual(report['upgrade_statistics']['total_upgrades'], 1)
        self.assertEqual(len(json.loads(self.planner.generate_report(report, 'json'))['available_upgrades']), 1)
        self.assertIn('4.17.20+4', self.planner.generate_report(report, 'text'))


if __name__ == '__main__':
    unittest.main()

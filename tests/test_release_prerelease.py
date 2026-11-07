import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/release-manager/version_bumper.py'
SPEC = importlib.util.spec_from_file_location('release_prerelease_under_test', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
Version, BumpType, PreReleaseType = MODULE.Version, MODULE.BumpType, MODULE.PreReleaseType


class PrereleaseVersionTests(unittest.TestCase):
    def test_documented_prerelease_transitions(self):
        cases = [('1.0.0-alpha.1', 'alpha', '1.0.0-alpha.2'),
                 ('1.0.0-alpha.5', 'beta', '1.0.0-beta.1'),
                 ('1.0.0-beta.3', 'rc', '1.0.0-rc.1')]
        for current, stage, expected in cases:
            with self.subTest(current=current, stage=stage):
                result = Version.parse(current).bump(BumpType.PATCH, PreReleaseType(stage))
                self.assertEqual(result.to_string(), expected)

    def test_same_stage_increments_counter_without_mutating_current(self):
        for stage in PreReleaseType:
            for number in [0, 1, 12]:
                with self.subTest(stage=stage, number=number):
                    current = Version.parse(f'3.2.7-{stage.value}.{number}')
                    result = current.bump(BumpType.PATCH, stage)
                    self.assertEqual(result.to_string(), f'3.2.7-{stage.value}.{number + 1}')
                    self.assertEqual(current.to_string(), f'3.2.7-{stage.value}.{number}')
                    self.assertIsNot(result, current)

    def test_forward_stage_change_resets_only_counter(self):
        for before, after in [('alpha', 'beta'), ('alpha', 'rc'), ('beta', 'rc')]:
            with self.subTest(before=before, after=after):
                result = Version.parse(f'3.2.7-{before}.12').bump(BumpType.PATCH, PreReleaseType(after))
                self.assertEqual(result.to_string(), f'3.2.7-{after}.1')

    def test_stable_version_starts_requested_prerelease(self):
        for bump, core in [(BumpType.MAJOR, '3.0.0'), (BumpType.MINOR, '2.5.0'),
                           (BumpType.PATCH, '2.4.7')]:
            for stage in PreReleaseType:
                with self.subTest(bump=bump, stage=stage):
                    result = Version.parse('2.4.6').bump(bump, stage)
                    self.assertEqual(result.to_string(), f'{core}-{stage.value}.1')

    def test_no_bump_preserves_stable_and_prerelease_versions(self):
        for text in ['2.4.6', '2.4.6-alpha.2', '2.4.6-beta.5', '2.4.6-rc.0']:
            for stage in [None, *PreReleaseType]:
                with self.subTest(current=text, stage=stage):
                    self.assertEqual(Version.parse(text).bump(BumpType.NONE, stage).to_string(), text)

    def test_existing_stable_promotion_is_preserved(self):
        for stage in PreReleaseType:
            for bump in [BumpType.PATCH, BumpType.MINOR, BumpType.MAJOR]:
                with self.subTest(stage=stage, bump=bump):
                    result = Version.parse(f'2.4.6-{stage.value}.2').bump(bump)
                    self.assertEqual(result.to_string(), '2.4.6')

    def test_json_cli_outputs_consistent_recommendation_and_snippets(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '-c', '1.0.0-alpha.1',
                                 '--prerelease', 'alpha', '--input-format', 'json',
                                 '--output-format', 'json', '--include-commands', '--include-files'],
                                input='[{"message":"fix: repair issue"}]', text=True,
                                capture_output=True, check=True)
        output = json.loads(result.stdout)
        self.assertEqual(output['recommended_version'], '1.0.0-alpha.2')
        self.assertEqual(output['recommended_version_with_v'], 'v1.0.0-alpha.2')
        self.assertEqual(output['bump_type'], 'patch')
        self.assertEqual(json.loads(output['file_updates']['package.json'])['version'], '1.0.0-alpha.2')
        self.assertIn('npm version 1.0.0-alpha.2 --no-git-tag-version', output['commands']['npm'])

    def test_git_log_cli_keeps_core_when_advancing_stage(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '-c', '1.0.0-beta.3',
                                 '--prerelease', 'rc', '--output-format', 'json'],
                                input='abcdef1 fix: repair issue\n', text=True,
                                capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)['recommended_version'], '1.0.0-rc.1')


if __name__ == '__main__':
    unittest.main()

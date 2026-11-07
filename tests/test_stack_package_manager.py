"""Stack commands must match the selected lockfile package manager."""
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'engineering/ci-cd-pipeline-builder/scripts/stack_detector.py'
spec = importlib.util.spec_from_file_location('tested_stack_detector', SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class StackPackageManagerTests(unittest.TestCase):
    def fixture(self, root, locks, scripts):
        (root / 'package.json').write_text(json.dumps({'scripts': scripts}))
        for lock in locks:
            (root / lock).write_text('')

    def test_all_lock_combinations_follow_precedence(self):
        locks = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
        for flags in itertools.product([False, True], repeat=3):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                selected = [lock for lock, enabled in zip(locks, flags) if enabled]
                self.fixture(root, selected, dict.fromkeys(['lint', 'test', 'build'], 'unused'))
                result = module.detect(root)
                manager = 'pnpm' if flags[2] else 'yarn' if flags[1] else 'npm'
                self.assertEqual(result.package_managers, [manager])
                self.assertEqual(result.lint_commands, [f'{manager} run lint'])
                self.assertEqual(result.test_commands, [f'{manager} test'])
                self.assertEqual(result.build_commands, [f'{manager} run build'])

    def test_only_present_scripts_are_emitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, ['pnpm-lock.yaml'], {'test': 'unused'})
            report = module.detect(root)
            self.assertEqual(report.test_commands, ['pnpm test'])
            self.assertEqual(report.lint_commands, [])
            self.assertEqual(report.build_commands, [])

    def test_mixed_stack_keeps_python_go_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, ['yarn.lock'], dict.fromkeys(['lint', 'test', 'build'], 'unused'))
            (root / 'requirements.txt').write_text('')
            (root / 'go.mod').write_text('module fixture')
            report = module.detect(root)
            self.assertEqual(report.test_commands, ['go test ./...', 'python3 -m pytest', 'yarn test'])
            self.assertEqual(report.package_managers, ['pip', 'yarn'])

    def test_cli_reports_selected_manager(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, ['pnpm-lock.yaml'], {'lint': 'unused', 'test': 'unused', 'build': 'unused'})
            result = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(root), '--format', 'json'], input='', text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['test_commands'], ['pnpm test'])
            self.assertEqual(report['build_commands'], ['pnpm run build'])


if __name__ == '__main__':
    unittest.main()

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/performance-profiler/scripts/performance_profiler.py'
spec = importlib.util.spec_from_file_location('profiler_build', SCRIPT)
profiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profiler)


class BuildArtifactsTests(unittest.TestCase):
    def put(self, root, name, size=1024):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'x' * size)

    def test_build_directories_are_counted(self):
        for directory in ['dist', 'build', '.next', 'out']:
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root, directory + '/static/bundle.js')
                result = profiler.bundle_indicators(root)
                self.assertEqual(result['build_dirs_present'], [directory])
                self.assertEqual(result['bundle_like_files'], 1)
                self.assertEqual(result['estimated_bundle_weight'], 1.0)

    def test_weights_and_nested_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root, 'packages/app/dist/main.js')
            self.put(root, '.next/static/style.css')
            self.put(root, 'build/main.js.map')
            self.put(root, 'src/main.ts')
            self.put(root, 'dist/image.png')
            result = profiler.bundle_indicators(root)
            self.assertEqual(result['bundle_like_files'], 4)
            self.assertEqual(result['estimated_bundle_weight'], 4.7)

    def test_default_scan_and_noise_exclusions_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root, 'src/main.js')
            self.put(root, 'dist/main.js')
            for directory in ['node_modules', '.git', 'coverage', '__pycache__']:
                self.put(root, directory + '/dist/noise.js')
                self.put(root, 'build/' + directory + '/noise.js')
            self.assertEqual(list(profiler.iter_files(root)), [root / 'src/main.js'])
            self.assertEqual(profiler.get_large_files(root, 1), [('src/main.js', 1024)])
            self.assertEqual(profiler.bundle_indicators(root)['bundle_like_files'], 2)

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root, 'dist/bundle.js', 2048)
            result = subprocess.run([sys.executable, str(SCRIPT), tmp, '--json'], capture_output=True, text=True, check=True)
            indicators = json.loads(result.stdout)['bundle_indicators']
            self.assertEqual(indicators['bundle_like_files'], 1)
            self.assertEqual(indicators['estimated_bundle_weight'], 2.0)


if __name__ == '__main__':
    unittest.main()

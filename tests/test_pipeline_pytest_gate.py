"""Regression checks for generated Python CI failure propagation, no shell execution."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "engineering/ci-cd-pipeline-builder/scripts/pipeline_generator.py"
spec = importlib.util.spec_from_file_location("pipeline_pytest_gate", SOURCE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class PythonGateTests(unittest.TestCase):
    def test_python_test_step_propagates_failure(self):
        for generator in (module.github_yaml, module.gitlab_yaml):
            for languages in (["python"], ["node", "python"], ["python", "go"]):
                with self.subTest(generator=generator.__name__, languages=languages):
                    output = generator({"languages": languages})
                    test_lines = [line.strip() for line in output.splitlines() if "python3 -m pytest" in line]
                    prefix = "- run: " if generator is module.github_yaml else "- "
                    self.assertEqual(test_lines, [prefix + "python3 -m pytest"])
                    self.assertIn("python3 -m pip install -r requirements.txt || true", output)

    def test_non_python_output_unchanged(self):
        for generator in (module.github_yaml, module.gitlab_yaml):
            for languages in ([], ["node"], ["go"], ["node", "go"]):
                self.assertNotIn("python3 -m pytest", generator({"languages": languages}))

    def test_cli_file_and_stdin_generate_unmasked_step(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = json.dumps({"languages": ["python"]})
            input_file = root / "stack.json"
            input_file.write_text(data, encoding="utf-8")
            for platform in ("github", "gitlab"):
                for use_file in (False, True):
                    with self.subTest(platform=platform, use_file=use_file):
                        args = [sys.executable, str(SOURCE), "--platform", platform, "--format", "json"]
                        if use_file:
                            args += ["--input", str(input_file)]
                        result = subprocess.run(args, input="" if use_file else data, capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn("python3 -m pytest", result.stdout)
                        self.assertNotIn("python3 -m pytest || true", result.stdout)
                        self.assertEqual(json.loads(result.stderr)["platform"], platform)


if __name__ == "__main__":
    unittest.main()

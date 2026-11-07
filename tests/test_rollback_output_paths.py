"""Runbook JSON and text outputs must not overwrite or relocate one another."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/migration-architect/scripts/rollback_generator.py"
PLAN = {"migration_id": "fixture", "migration_type": "database",
        "phases": [{"name": "preparation", "duration_hours": 2, "risk_level": "low"}]}


class RollbackOutputPathsTests(unittest.TestCase):
    def run_cli(self, folder, output, fmt):
        source = folder / "plan.json"
        encoded = json.dumps(PLAN)
        source.write_text(encoded, encoding="utf-8")
        args = [sys.executable, "-B", str(SCRIPT), "--input", str(source), "--format", fmt]
        if output is not None:
            args += ["--output", str(output)]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source.read_text(encoding="utf-8"), encoded)
        return result

    def test_both_outputs_remain_distinct_for_every_suffix(self):
        for name in ("runbook", "runbook.txt", "runbook.JSON", "runbook.json", "runbook.json.backup"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                output = folder / name
                self.run_cli(folder, output, "both")
                self.assertEqual(json.loads(output.read_text())["migration_id"], "fixture")
                text_name = name[:-5] + ".txt" if name.endswith(".json") else name + ".txt"
                self.assertIn("ROLLBACK RUNBOOK:", (folder / text_name).read_text())
                self.assertEqual({p.name for p in folder.iterdir()}, {"plan.json", name, text_name})

    def test_json_named_directory_stays_unchanged(self):
        for fmt in ("both", "text"):
            with self.subTest(format=fmt), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                folder = root / "archive.json"
                folder.mkdir()
                decoy = root / "archive.txt"
                decoy.mkdir()
                sentinel = decoy / "runbook.txt"
                sentinel.write_text("preserve me")
                self.run_cli(folder, folder / "runbook.json", fmt)
                self.assertIn("ROLLBACK RUNBOOK:", (folder / "runbook.txt").read_text())
                self.assertEqual(sentinel.read_text(), "preserve me")

    def test_single_formats_keep_requested_destinations(self):
        for fmt in ("json", "text"):
            for name in ("runbook", "runbook.txt", "runbook.JSON", "runbook.json"):
                with self.subTest(format=fmt, name=name), tempfile.TemporaryDirectory() as directory:
                    folder = Path(directory)
                    self.run_cli(folder, folder / name, fmt)
                    expected = name[:-5] + ".txt" if fmt == "text" and name.endswith(".json") else name
                    body = (folder / expected).read_text()
                    if fmt == "json":
                        self.assertEqual(json.loads(body)["migration_id"], "fixture")
                    else:
                        self.assertIn("ROLLBACK RUNBOOK:", body)
                    self.assertEqual({p.name for p in folder.iterdir()}, {"plan.json", expected})

    def test_stdout_modes_unchanged(self):
        for fmt in ("json", "text", "both"):
            with self.subTest(format=fmt), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                result = self.run_cli(folder, None, fmt)
                if fmt == "json":
                    self.assertEqual(json.loads(result.stdout)["migration_id"], "fixture")
                else:
                    self.assertIn("ROLLBACK RUNBOOK:", result.stdout)
                self.assertEqual({p.name for p in folder.iterdir()}, {"plan.json"})


if __name__ == "__main__":
    unittest.main()

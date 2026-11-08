"""Forced TC configuration initialization must preserve existing registries."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/tc-tracker/scripts/tc_init.py"


class PreserveRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tc = self.root / "docs/TC"
        self.tc.mkdir(parents=True)
        self.config = self.tc / "tc_config.json"
        self.registry = self.tc / "tc_registry.json"

    def seed(self, config=True):
        if config:
            self.config.write_text(json.dumps({"project_name": "Fixture", "default_author": "Custom"}))
        registry = {"project_name": "Fixture", "created": "2020-01-01T00:00:00Z", "updated": "2026-01-01T00:00:00Z",
                    "next_tc_number": 42, "records": [{"tc_id": "TC-041-01-01-26-example", "status": "tested"}],
                    "statistics": {"total": 1, "by_status": {"tested": 1}}, "custom_field": "한글"}
        self.registry.write_text(json.dumps(registry, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        return self.registry.read_bytes(), self.registry.stat().st_mtime_ns

    def run_init(self, force=False, as_json=True):
        args = [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), "--project", "Fixture"]
        if force:
            args.append("--force")
        if as_json:
            args.append("--json")
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if as_json else result.stdout

    def assert_preserved(self, before):
        self.assertEqual((self.registry.read_bytes(), self.registry.stat().st_mtime_ns), before)

    def test_force_preserves_registry_and_refreshes_config(self):
        before = self.seed()
        self.assertEqual(self.run_init(force=True)["status"], "initialized")
        self.assert_preserved(before)
        self.assertEqual(json.loads(self.config.read_text())["default_author"], "Claude")

    def test_force_without_config_preserves_existing_registry(self):
        before = self.seed(config=False)
        self.run_init(force=True)
        self.assert_preserved(before)
        self.assertTrue(self.config.is_file())

    def test_normal_init_without_config_preserves_registry(self):
        before = self.seed(config=False)
        self.run_init()
        self.assert_preserved(before)

    def test_normal_repeated_init_preserves_all_existing_data(self):
        before = self.seed()
        config_before = self.config.read_bytes(), self.config.stat().st_mtime_ns
        self.assertEqual(self.run_init()["status"], "already_initialized")
        self.assert_preserved(before)
        self.assertEqual((self.config.read_bytes(), self.config.stat().st_mtime_ns), config_before)

    def test_missing_registry_is_created_with_or_without_force(self):
        for force in [False, True]:
            with self.subTest(force=force), tempfile.TemporaryDirectory() as directory:
                self.root = Path(directory)
                self.tc = self.root / "docs/TC"
                self.registry = self.tc / "tc_registry.json"
                self.run_init(force=force)
                data = json.loads(self.registry.read_text())
                self.assertEqual(data["records"], [])
                self.assertEqual(data["next_tc_number"], 1)
                self.assertEqual(data["statistics"]["total"], 0)

    def test_force_preserves_unreadable_registry_bytes(self):
        self.registry.write_bytes(b"not valid JSON\xff\n")
        before = self.registry.read_bytes(), self.registry.stat().st_mtime_ns
        self.run_init(force=True)
        self.assert_preserved(before)

    def test_record_and_evidence_files_remain_unchanged(self):
        before = self.seed()
        paths = [self.tc / "records/existing/tc_record.json", self.tc / "evidence/existing.txt"]
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Existing fixture content\x00")
        contents = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        self.run_init(force=True)
        self.assert_preserved(before)
        self.assertEqual(contents, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})

    def test_human_output_and_repeated_force_preserve_registry(self):
        before = self.seed()
        self.assertIn("Initialized TC tracking", self.run_init(force=True, as_json=False))
        self.assert_preserved(before)
        self.run_init(force=True)
        self.assert_preserved(before)


if __name__ == "__main__":
    unittest.main()

"""Comparator dataclasses must be serializable when generating migration hashes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, is_dataclass

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/database-designer/migration_generator.py"
spec = importlib.util.spec_from_file_location("database_migration_hash", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def schema(columns=None):
    return {"tables": {"items": {"columns": columns or {"id": {"type": "INT"}}}}}


def changes(before, after):
    comparator = module.SchemaComparator()
    comparator.load_schemas(before, after)
    return comparator.compare_schemas()


def normalized(value):
    if is_dataclass(value):
        return normalized(asdict(value))
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


class DatabaseMigrationHashTests(unittest.TestCase):
    def test_dataclass_change_kinds(self):
        base = schema()
        added = schema({"id": {"type": "INT"}, "label": {"type": "TEXT"}})
        modified = schema({"id": {"type": "BIGINT"}})
        for before, after in [({"tables": {}}, base), (base, {"tables": {}}),
                              (base, added), (added, base), (base, modified)]:
            for zero_downtime in (False, True):
                with self.subTest(before=before, after=after, zero_downtime=zero_downtime):
                    diff = changes(before, after)
                    original = copy.deepcopy(diff)
                    plan = module.MigrationGenerator(zero_downtime).generate_migration(diff)
                    expected = hashlib.md5(json.dumps(normalized(diff), sort_keys=True).encode()).hexdigest()
                    self.assertEqual(plan.migration_id, expected[:8])
                    self.assertEqual(plan.source_schema_hash, expected)
                    self.assertTrue(plan.steps)
                    self.assertEqual(diff, original)
                    json.dumps(asdict(plan))

    def test_plain_changes_keep_original_hash(self):
        before = schema()
        after = copy.deepcopy(before)
        after["tables"]["items"]["indexes"] = [{"name": "idx_id", "columns": ["id"]}]
        diff = changes(before, after)
        expected = hashlib.md5(json.dumps(diff, sort_keys=True).encode()).hexdigest()
        plan = module.MigrationGenerator().generate_migration(diff)
        self.assertEqual(plan.migration_id, expected[:8])
        self.assertEqual(plan.source_schema_hash, expected)

    def test_cli_formats_and_validation_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            before, after = root / "before.json", root / "after.json"
            before.write_text(json.dumps(schema()), encoding="utf-8")
            after.write_text(json.dumps(schema({"id": {"type": "BIGINT"}})), encoding="utf-8")
            for extra in (["--format", "json"], ["--format", "text"], ["--format", "sql"],
                          ["--validate-only"], ["--format", "json", "--zero-downtime"]):
                with self.subTest(extra=extra):
                    run = subprocess.run([sys.executable, "-B", str(SCRIPT), "--current", str(before),
                                          "--target", str(after), *extra], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertTrue(run.stdout.strip())
                    self.assertEqual(run.stderr, "")


if __name__ == "__main__":
    unittest.main()

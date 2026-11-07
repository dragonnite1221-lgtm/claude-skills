"""API operation removals must fail compatibility without treating metadata as verbs."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/migration-architect/scripts/compatibility_checker.py"
spec = importlib.util.spec_from_file_location("api_operation_removal", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
METADATA = {"parameters": [{"name": "id", "in": "query"}], "summary": "Items",
            "description": "Description", "servers": [{"url": "https://example.invalid"}],
            "$ref": "#/components/pathItems/Shared", "x-feature": "fixture"}


def report(before, after):
    return module.SchemaCompatibilityChecker().analyze_api_schema(before, after)


class ApiOperationRemovalTests(unittest.TestCase):
    def test_each_removed_method_on_retained_path(self):
        for method in METHODS:
            with self.subTest(method=method):
                survivor = "post" if method == "get" else "get"
                before = {"paths": {"/items": {method: {}, survivor: {}}}}
                after = {"paths": {"/items": {survivor: {}}}}
                original = copy.deepcopy((before, after))
                result = report(before, after)
                self.assertEqual(result.overall_compatibility, "breaking_changes")
                self.assertEqual(result.breaking_changes_count, 1)
                self.assertEqual(result.issues[0].affected_operations, [f"{method.upper()} /items"])
                self.assertEqual(result.issues[0].field_path, f"paths./items.{method}")
                self.assertEqual((before, after), original)

    def test_removed_path_reports_only_operations(self):
        before = {"paths": {"/items": dict(METADATA, **{m: {} for m in METHODS})}}
        result = report(before, {"paths": {}})
        self.assertEqual(result.breaking_changes_count, len(METHODS))
        self.assertEqual({i.affected_operations[0] for i in result.issues},
                         {f"{m.upper()} /items" for m in METHODS})

    def test_metadata_is_not_an_operation(self):
        schema = {"paths": {"/items": dict(METADATA, get={})}}
        result = report(schema, copy.deepcopy(schema))
        self.assertEqual(result.issues, [])
        self.assertEqual(result.overall_compatibility, "fully_compatible")
        self.assertEqual(report(schema, {"paths": {"/items": {"get": {}}}}).issues, [])

    def test_added_operation_and_existing_parameter_checks(self):
        before = {"paths": {"/items": {"get": {}}}}
        self.assertEqual(report(before, {"paths": {"/items": {"get": {}, "post": {}}}}).issues, [])
        after = {"paths": {"/items": {"get": {"parameters": [{"name": "id", "required": True}]}}}}
        self.assertEqual(report(before, after).issues[0].type, "required_parameter_added")

    def test_cli_removed_method_exit_and_formats(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder) / name for name in ("before.json", "after.json")]
            for path, methods in zip(paths, ({"get": {}, "post": {}}, {"get": {}})):
                path.write_text(json.dumps({"paths": {"/items": methods}}))
            for fmt in ("json", "text", "both"):
                with self.subTest(format=fmt):
                    run = subprocess.run([sys.executable, "-B", str(SCRIPT), "--before", str(paths[0]),
                                          "--after", str(paths[1]), "--type", "api", "--format", fmt],
                                         capture_output=True, text=True)
                    self.assertEqual(run.returncode, 2, run.stderr)
                    self.assertEqual(run.stderr, "")
                    self.assertIn("POST /items", run.stdout)
                    if fmt == "json":
                        self.assertEqual(json.loads(run.stdout)["breaking_changes_count"], 1)


if __name__ == "__main__":
    unittest.main()

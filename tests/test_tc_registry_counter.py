"""JSON booleans are not valid sequential TC counters."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/tc-tracker/scripts/tc_validator.py"


class CounterTests(unittest.TestCase):
    def validate(self, value, as_json=True, bad_status=False):
        registry = {"project_name": "Fixture", "created": "2026-11-08T00:00:00+00:00",
                    "updated": "2026-11-08T00:00:00+00:00", "next_tc_number": value,
                    "records": [], "statistics": {}}
        if bad_status:
            registry["records"].append({"tc_id": "TC-001-11-08-26-example", "title": "Example",
                "status": "unknown", "scope": "feature", "priority": "medium",
                "created": registry["created"], "updated": registry["updated"], "path": "record.json"})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            before = path.read_bytes()
            command = [sys.executable, str(SCRIPT), "--registry", str(path)]
            if as_json:
                command.append("--json")
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.stderr, "")
            self.assertEqual(path.read_bytes(), before)
        return result.returncode, json.loads(result.stdout) if as_json else result.stdout

    def assert_counter_error(self, value):
        code, result = self.validate(value)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["error_count"], 1)
        self.assertIn("next_tc_number must be a positive integer", result["errors"][0])

    def test_true_is_invalid(self):
        self.assert_counter_error(True)

    def test_false_remains_invalid(self):
        self.assert_counter_error(False)

    def test_positive_integer_controls(self):
        for value in (1, 2, 999, 10 ** 20):
            with self.subTest(value=value):
                code, result = self.validate(value)
                self.assertEqual(code, 0)
                self.assertEqual(result["errors"], [])

    def test_nonpositive_integers(self):
        for value in (0, -1):
            with self.subTest(value=value):
                self.assert_counter_error(value)

    def test_other_json_types_remain_invalid(self):
        for value in (1.0, 1.5, "1", None, [], {}):
            with self.subTest(value=value):
                self.assert_counter_error(value)

    def test_text_output(self):
        code, output = self.validate(True, as_json=False)
        self.assertEqual(code, 1)
        self.assertIn("VALIDATION ERRORS (1)", output)
        self.assertIn("next_tc_number", output)

    def test_later_registry_errors_are_still_collected(self):
        code, result = self.validate(True, bad_status=True)
        self.assertEqual(code, 1)
        self.assertEqual(result["error_count"], 2)
        self.assertIn("records[0].status", result["errors"][1])


if __name__ == "__main__":
    unittest.main()

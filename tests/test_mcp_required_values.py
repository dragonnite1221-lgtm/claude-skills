"""Malformed required entries must produce validation output, not tracebacks."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "engineering" /
          "mcp-server-builder" / "scripts" / "mcp_validator.py")


class RequiredValueTests(unittest.TestCase):
    def validate(self, required, strict=True, output_format="json", file_input=False):
        payload = {"tools": [{"name": "read_record", "description": "Read a record by ID",
                             "inputSchema": {"type": "object", "properties": {
                                 "id": {"type": "string"}}, "required": required}}]}
        command = [sys.executable, str(SCRIPT), "--format", output_format]
        if strict:
            command.append("--strict")
        with tempfile.TemporaryDirectory() as directory:
            data = json.dumps(payload)
            if file_input:
                source = Path(directory) / "manifest.json"
                source.write_text(data, encoding="utf-8")
                command += ["--input", str(source)]
                data = None
            result = subprocess.run(command, input=data, text=True,
                                    capture_output=True, check=False)
        self.assertEqual(result.stderr, "")
        return result

    def assert_errors(self, required, count, strict=True, file_input=False):
        result = self.validate(required, strict=strict, file_input=file_input)
        self.assertEqual(result.returncode, int(strict and count > 0))
        report = json.loads(result.stdout)
        self.assertEqual(len(report["errors"]), count)
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["tool_count"], 1)
        return report

    def test_object_required_entry(self):
        self.assert_errors([{}], 1)

    def test_array_required_entry(self):
        self.assert_errors([[]], 1)

    def test_nested_mixed_values_continue_validation(self):
        self.assert_errors(["id", {"name": "id"}, ["id"], "missing"], 3)

    def test_non_strict_still_emits_errors(self):
        self.assert_errors([{}], 1, strict=False)

    def test_text_file_input_reports_all_errors(self):
        result = self.validate([{}, [], "missing"], output_format="text", file_input=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("- errors: 3", result.stdout)
        self.assertIn("required field 'missing'", result.stdout)

    def test_valid_required_values(self):
        self.assert_errors(["id"], 0)

    def test_missing_required_value_keeps_diagnostic(self):
        report = self.assert_errors(["missing"], 1)
        self.assertEqual(report["errors"], [
            "read_record: required field 'missing' is not defined in properties."])

    def test_other_json_scalars_are_reported(self):
        self.assert_errors([None, True, 1, 1.5], 4)


if __name__ == "__main__":
    unittest.main()

"""Single-record status must not arbitrarily select an ambiguous prefix."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/tc-tracker/scripts/tc_status.py"


class StatusResolutionTests(unittest.TestCase):
    def query(self, names, query, as_json=True, incomplete=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tc = root / "docs/TC"
            tc.mkdir(parents=True)
            (tc / "tc_registry.json").write_text('{"project_name": "Fixture"}')
            for name in names:
                target = tc / "records" / name / "tc_record.json"
                target.parent.mkdir(parents=True)
                target.write_text(json.dumps({"tc_id": name, "title": name,
                                               "status": "planned"}))
            for name in incomplete:
                (tc / "records" / name).mkdir(parents=True)
            before = {str(p.relative_to(root)): p.read_bytes()
                      for p in root.rglob("*") if p.is_file()}
            command = [sys.executable, str(SCRIPT), "--root", directory, "--tc-id", query]
            if as_json:
                command.append("--json")
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.stderr, "")
            after = {str(p.relative_to(root)): p.read_bytes()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(after, before)
        return result.returncode, json.loads(result.stdout) if as_json else result.stdout

    def test_ambiguous_prefix_in_both_creation_orders(self):
        names = ["TC-001-04-05-26-alpha", "TC-002-04-05-26-beta"]
        for order in (names, names[::-1]):
            with self.subTest(order=order):
                code, result = self.query(order, "TC-00")
                self.assertEqual(code, 2)
                self.assertEqual(result["status"], "error")
                self.assertNotIn("record", result)
                self.assertIn("ambiguous", result["error"])

    def test_ambiguous_text_does_not_display_a_record(self):
        code, text = self.query(["TC-001-alpha", "TC-001-beta"], "TC-001", False)
        self.assertEqual(code, 2)
        self.assertTrue(text.startswith("ERROR:"))
        self.assertNotIn("Title:", text)

    def test_exact_directory_takes_precedence(self):
        code, result = self.query(["TC-001", "TC-001-extra"], "TC-001")
        self.assertEqual(code, 0)
        self.assertEqual(result["record"]["tc_id"], "TC-001")

    def test_unique_prefix(self):
        code, result = self.query(["TC-001-alpha", "TC-002-beta"], "TC-001")
        self.assertEqual(code, 0)
        self.assertEqual(result["record"]["tc_id"], "TC-001-alpha")

    def test_incomplete_directory_is_not_a_match(self):
        code, result = self.query(["TC-001-alpha"], "TC-001", incomplete=["TC-001-draft"])
        self.assertEqual(code, 0)
        self.assertEqual(result["record"]["tc_id"], "TC-001-alpha")

    def test_missing_prefix(self):
        self.assertEqual(self.query(["TC-001-alpha"], "TC-999")[0], 2)

    def test_missing_records_directory(self):
        self.assertEqual(self.query([], "TC-001")[0], 2)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/data-quality-auditor/scripts/missing_value_analyzer.py"
spec = importlib.util.spec_from_file_location("missing_csv_fields", SCRIPT)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)


class MissingCsvFieldsTests(unittest.TestCase):
    def test_none_and_missing_strings_are_null(self):
        for value in [None, "", "NULL", " N/A ", "nan", "undefined", "missing"]:
            with self.subTest(value=value):
                self.assertTrue(analyzer.is_null(value))
        for value in ["0", "false", "none of these", "x"]:
            with self.subTest(value=value):
                self.assertFalse(analyzer.is_null(value))

    def test_omitted_trailing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "short.csv"
            path.write_text("id,age,active\n1,20,true\n2\n3,30\n", encoding="utf-8")
            headers, rows = analyzer.load_csv(str(path))
            self.assertIsNone(rows[1]["age"])
            self.assertIsNone(rows[2]["active"])
            masks = analyzer.compute_null_mask(headers, rows)
            self.assertEqual(masks, {"id": [False] * 3, "age": [False, True, False],
                                     "active": [False, True, True]})
            self.assertEqual(analyzer.infer_type([row["age"] for row in rows]), "int")
            self.assertEqual(analyzer.infer_type([row["active"] for row in rows]), "bool")
            self.assertEqual(analyzer.compute_cooccurrence(headers, masks),
                             [{"col_a": "age", "col_b": "active", "co_null_rows": 1}])

    def test_all_omitted_column_has_no_type_observations(self):
        self.assertEqual(analyzer.infer_type([None, None]), "string")
        masks = analyzer.compute_null_mask(["field"], [{"field": None}, {}])
        self.assertEqual(analyzer.null_stats(masks["field"]), {"count": 2, "pct": 100.0})

    def test_cli_json_and_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "short.csv"
            path.write_text("id,age,active\n1,20,true\n2\n3,30\n", encoding="utf-8")
            for fmt in ["json", "text"]:
                with self.subTest(fmt=fmt):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), "--file", str(path), "--format", fmt],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    if fmt == "json":
                        output = json.loads(result.stdout)
                        self.assertEqual(output["total_rows"], 3)
                        columns = {entry["column"]: entry for entry in output["columns"]}
                        self.assertEqual(columns["age"]["null_count"], 1)
                        self.assertEqual(columns["age"]["null_pct"], 33.33)
                        self.assertEqual(columns["active"]["null_count"], 2)
                        self.assertEqual(columns["active"]["null_pct"], 66.67)
                    else:
                        self.assertIn("Fully complete columns: 1/3", result.stdout)
                        self.assertIn("Nulls: 2 (66.67%)", result.stdout)
                        self.assertIn("age + active", result.stdout)


if __name__ == "__main__":
    unittest.main()

"""RICE CSV output must preserve quoted fields and prioritized values."""

import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "product-team/product-manager-toolkit/scripts/rice_prioritizer.py"
FIELDS = ["name", "reach", "impact", "confidence", "effort", "description"]


class RiceCsvQuotingTests(unittest.TestCase):
    def run_fixture(self, rows, output="csv"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "features.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            result = subprocess.run([sys.executable, "-B", str(SOURCE), str(path), "--output", output],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            return result.stdout

    def feature(self, name, description="", reach=100):
        return dict(zip(FIELDS, [name, str(reach), "high", "high", "s", description]))

    def test_commas_round_trip(self):
        source = self.feature("Search, export", "CSV, JSON, and text")
        row = list(csv.DictReader(io.StringIO(self.run_fixture([source]), newline="")))[0]
        self.assertEqual({key: row[key] for key in FIELDS}, source)
        self.assertEqual(row["rice_score"], "66.67")
        self.assertNotIn(None, row)

    def test_quotes_round_trip(self):
        source = self.feature('The "best" option', '"quoted", with comma')
        rows = list(csv.DictReader(io.StringIO(self.run_fixture([source]), newline="")))
        self.assertEqual(len(rows), 1)
        self.assertEqual({key: rows[0][key] for key in FIELDS}, source)

    def test_multiline_fields_remain_one_record(self):
        source = self.feature("Line one\nLine two", "Paragraph one\nParagraph two")
        rows = list(csv.DictReader(io.StringIO(self.run_fixture([source]), newline="")))
        self.assertEqual(len(rows), 1)
        self.assertEqual({key: rows[0][key] for key in FIELDS}, source)

    def test_unicode_and_empty_description(self):
        source = self.feature("검색 🔎, 내보내기")
        rows = list(csv.DictReader(io.StringIO(self.run_fixture([source]), newline="")))
        self.assertEqual({key: rows[0][key] for key in FIELDS}, source)

    def test_csv_order_and_values_match_json(self):
        source = [self.feature("Low, score", "first", 30), self.feature('High "score"', "second", 300)]
        csv_rows = list(csv.DictReader(io.StringIO(self.run_fixture(source), newline="")))
        json_rows = json.loads(self.run_fixture(source, "json"))["features"]
        self.assertEqual(csv_rows, [{key: str(value) for key, value in row.items()} for row in json_rows])
        self.assertEqual([row["name"] for row in csv_rows], ['High "score"', "Low, score"])

    def test_empty_portfolio_still_outputs_nothing(self):
        self.assertEqual(self.run_fixture([]), "")

    def test_default_demo_csv_header(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "--output", "csv"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        reader = csv.DictReader(io.StringIO(result.stdout, newline=""))
        self.assertEqual(reader.fieldnames, [*FIELDS[:-1], "rice_score"])
        self.assertEqual(len(list(reader)), 5)

    def test_help(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--output", result.stdout)


if __name__ == "__main__":
    unittest.main()

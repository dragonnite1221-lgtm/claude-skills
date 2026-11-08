"""Assumption plans retain CSV field boundaries and multiline content."""
import csv
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "product-team/product-discovery/scripts/assumption_mapper.py"
HEADER = ["rank", "priority_score", "category", "risk", "certainty", "test", "assumption"]


class AssumptionCsvTests(unittest.TestCase):
    def run_plan(self, args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        title, data = result.stdout.decode("utf-8").split("\n", 1)
        self.assertEqual(title, "prioritized_assumption_test_plan")
        rows = list(csv.reader(io.StringIO(data, newline="")))
        self.assertEqual(rows[0], HEADER)
        self.assertTrue(all(len(row) == 7 for row in rows))
        return rows[1:]

    def test_inline_commas_and_quotes_round_trip(self):
        for statement in ["Users want fast, reliable search", '"Quoted" assumption', 'A "quote", and comma']:
            with self.subTest(statement=statement):
                rows = self.run_plan(["--assumption", statement + "|desirability|.9|.1"])
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][-1], statement)

    def test_inline_line_endings_round_trip(self):
        for statement in ["First\nsecond", "First\rsecond", "First\r\nsecond"]:
            with self.subTest(statement=statement):
                rows = self.run_plan(["--assumption", statement + "|viability|1|0"])
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][-1], statement)

    def test_csv_input_preserves_embedded_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "한글 assumptions.csv"
            statement = 'Users say "yes",\r\nthen ask for 검색'
            category = "custom,\ncategory"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["assumption", "category", "risk", "certainty"])
                writer.writerow([statement, category, ".8", ".25"])
            before = path.read_bytes(), path.stat().st_mtime_ns
            rows = self.run_plan([str(path)])
            self.assertEqual(rows[0][2], category)
            self.assertEqual(rows[0][-1], statement)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_numeric_precision_and_recommendation_are_unchanged(self):
        rows = self.run_plan(["--assumption", "Simple|desirability|.9|.1"])
        self.assertEqual(rows, [["1", "0.8100", "desirability", "0.90", "0.10",
                                 "problem interviews or fake-door test", "Simple"]])

    def test_ranking_and_top_limit_are_unchanged(self):
        rows = self.run_plan(["--assumption", "Low, priority|viability|.1|0",
                              "--assumption", "High, priority|feasibility|1|0", "--top", "1"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][-1], "High, priority")
        self.assertEqual(rows[0][5], "technical spike or architecture prototype")

    def test_equal_scores_keep_input_order(self):
        rows = self.run_plan(["--assumption", 'First "one"|usability|.5|0',
                              "--assumption", 'Second "two"|usability|.5|0'])
        self.assertEqual([row[-1] for row in rows], ['First "one"', 'Second "two"'])

    def test_zero_top_emits_only_header(self):
        self.assertEqual(self.run_plan(["--assumption", "Ignored|viability|1|0", "--top", "0"]), [])

    def test_empty_statement_and_unicode_category_round_trip(self):
        rows = self.run_plan(["--assumption", '|기타 "분류", custom|.5|.2'])
        self.assertEqual(rows[0][-1], "")
        self.assertEqual(rows[0][2], '기타 "분류", custom')


if __name__ == "__main__":
    unittest.main()

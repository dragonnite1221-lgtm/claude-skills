import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "finance/saas-metrics-coach/scripts/unit_economics_simulator.py"
SPEC = importlib.util.spec_from_file_location("economics_report_rows", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row_months(report):
    return [int(value) for value in re.findall(r"^\s*(\d+)\s+\$", report, re.MULTILINE)]


class ReportRowTests(unittest.TestCase):
    def result(self, months):
        return MODULE.simulate(50000, 10, 3, 2000, months=months)

    def cli(self, *extra):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--mrr=50000", "--growth=10", "--churn=3", "--cac=2000", *extra], capture_output=True, text=True)

    def test_short_horizons_show_each_month_once(self):
        for months in range(1, 7):
            with self.subTest(months=months):
                self.assertEqual(row_months(MODULE.format_report(self.result(months))), list(range(1, months + 1)))

    def test_long_horizons_keep_first_and_last_three(self):
        for months in (7, 12, 24):
            with self.subTest(months=months):
                self.assertEqual(row_months(MODULE.format_report(self.result(months))), [1, 2, 3, months - 2, months - 1, months])

    def test_ellipsis_only_when_rows_are_omitted(self):
        for months in (1, 3, 4, 6, 7, 12):
            with self.subTest(months=months):
                report = MODULE.format_report(self.result(months))
                self.assertEqual(report.count("  ...\n"), int(months > 6))

    def test_short_horizon_cli_rows(self):
        for months in (1, 4):
            with self.subTest(months=months):
                result = self.cli("--months=" + str(months))
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                self.assertEqual(row_months(result.stdout), list(range(1, months + 1)))

    def test_default_cli_selection(self):
        result = self.cli()
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertEqual(row_months(result.stdout), [1, 2, 3, 10, 11, 12])

    def test_json_contains_all_projections(self):
        result = self.cli("--months=4", "--json")
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        data = json.loads(result.stdout)
        self.assertEqual([p["month"] for p in data["projections"]], [1, 2, 3, 4])
        self.assertEqual(data, self.result(4))

    def test_formatting_preserves_input(self):
        result = self.result(4)
        original = copy.deepcopy(result)
        MODULE.format_report(result)
        self.assertEqual(result, original)

    def test_report_keeps_non_table_sections(self):
        report = MODULE.format_report(self.result(4))
        for section in ("📊 INPUTS", "📈 12-MONTH SUMMARY", "📅 MONTHLY PROJECTIONS"):
            self.assertEqual(report.count(section), 1)
        self.assertIn("Starting MRR: $50,000", report)
        self.assertIn("CAC: $2,000", report)


if __name__ == "__main__":
    unittest.main()

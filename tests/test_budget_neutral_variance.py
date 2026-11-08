"""Zero budget differences are neutral throughout reports."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / (
    "finance/financial-analyst/scripts/budget_variance_analyzer.py"
)
SPEC = importlib.util.spec_from_file_location("budget_analyzer", SCRIPT)
BUDGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUDGET)


def analyze(items, **kwargs):
    analyzer = BUDGET.BudgetVarianceAnalyzer({"line_items": items}, **kwargs)
    return analyzer, analyzer.run_analysis()


def item(kind, actual, budget=100, department="Operations"):
    return {"name": kind, "type": kind, "actual": actual,
            "budget": budget, "department": department}


class NeutralVarianceTests(unittest.TestCase):
    def test_equal_budget_all_type_aliases(self):
        for kind in ["revenue", "income", "sales", "REVENUE", "expense", "cost"]:
            with self.subTest(kind=kind):
                _, result = analyze([item(kind, 100)])
                self.assertEqual(result["all_variances"][0]["favorability"], "Neutral")

    def test_signed_zero_and_negative_budgets(self):
        for value in [0, -0.0, -100, 0.5]:
            _, result = analyze([item("expense", value, value)])
            self.assertEqual(result["executive_summary"]["neutral_count"], 1)
            self.assertEqual(result["executive_summary"]["unfavorable_count"], 0)

    def test_nonzero_favorability_is_preserved(self):
        _, result = analyze([item("revenue", 110), item("revenue", 90),
                             item("expense", 90), item("expense", 110)])
        self.assertEqual([v["favorability"] for v in result["all_variances"]],
                         ["Favorable", "Unfavorable", "Favorable", "Unfavorable"])
        self.assertEqual(result["executive_summary"]["neutral_count"], 0)

    def test_counts_partition_mixed_rows(self):
        _, result = analyze([item("revenue", 100), item("expense", 100),
                             item("revenue", 110), item("expense", 110)])
        for summary in [result["executive_summary"],
                        result["department_summary"]["Operations"]]:
            self.assertEqual(summary["favorable_count"], 1)
            self.assertEqual(summary["unfavorable_count"], 1)
            self.assertEqual(summary["neutral_count"], 2)
        self.assertEqual(result["executive_summary"]["net_impact"], 0)

    def test_materiality_is_independent_from_neutrality(self):
        _, result = analyze([item("expense", 100)], threshold_pct=0)
        self.assertEqual(len(result["material_variances"]), 1)
        self.assertEqual(result["material_variances"][0]["favorability"], "Neutral")

    def test_empty_dataset_counts(self):
        _, result = analyze([])
        for key in ["favorable_count", "unfavorable_count", "neutral_count"]:
            self.assertEqual(result["executive_summary"][key], 0)
        self.assertEqual(result["department_summary"], {})

    def test_text_reports_neutral_counts(self):
        analyzer, result = analyze([item("income", 100), item("expense", 100)])
        report = analyzer.format_text(result)
        self.assertIn("Unfavorable: 0  |  Neutral: 2", report)
        self.assertIn("Fav: 0 / Unfav: 0 / Neutral: 2", report)

    def test_file_cli_json_and_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "budget.json"
            path.write_text(json.dumps({"line_items": [item("sales", 100)]}))
            for mode in ["json", "text"]:
                result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path),
                                         "--format", mode], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if mode == "json":
                    self.assertEqual(json.loads(result.stdout)["executive_summary"]
                                     ["neutral_count"], 1)
                else:
                    self.assertIn("Unfavorable: 0  |  Neutral: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()

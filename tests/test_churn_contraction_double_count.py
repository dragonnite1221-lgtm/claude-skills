"""Gross revenue churn must not count contraction again after full churn."""
from datetime import date
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/cro-advisor/scripts/churn_analyzer.py'
SPEC = importlib.util.spec_from_file_location('churn_contraction_tool', SCRIPT)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)
START, END = date(2024, 3, 1), date(2024, 3, 31)


def customer(id, arr=100, churn=None, contraction=0, start='2024-01-01', expansion=0):
    return TOOL.Customer(id, id, 'SMB', arr, start, churn, expansion, contraction)


def rate(*customers):
    return TOOL.RetentionAnalyzer(list(customers)).revenue_churn_rate(START, END)


class ChurnContractionTests(unittest.TestCase):
    def test_churned_contraction_not_counted_twice(self):
        gone = customer('gone', churn='2024-03-15', contraction=25)
        stays = customer('stays', contraction=10)
        self.assertEqual(rate(gone, stays), 0.55)

    def test_full_churn_is_one_hundred_percent(self):
        self.assertEqual(rate(customer('gone', churn='2024-03-15', contraction=25)), 1)

    def test_active_contraction_still_counts(self):
        self.assertEqual(rate(customer('stays', contraction=25, expansion=50)), 0.25)

    def test_future_churn_still_counts_contraction(self):
        self.assertEqual(rate(customer('future', churn='2024-04-01', contraction=25)), 0.25)

    def test_churn_at_period_end_excludes_contraction(self):
        self.assertEqual(rate(customer('gone', churn='2024-03-31', contraction=25)), 1)

    def test_preopening_churn_and_new_customer_excluded(self):
        self.assertEqual(rate(customer('stays'), customer('old', churn='2024-03-01', contraction=25),
                              customer('new', start='2024-03-02', contraction=25)), 0)

    def test_empty_and_zero_opening_are_safe(self):
        self.assertEqual(rate(), 0)
        self.assertEqual(rate(customer('zero', arr=0)), 0)

    def test_revenue_churn_agrees_with_gross_retention(self):
        customers = [customer('gone', churn='2024-03-15', contraction=25),
                     customer('stays', contraction=10, expansion=50)]
        analyzer = TOOL.RetentionAnalyzer(customers)
        waterfall = analyzer.arr_waterfall(START, END)
        self.assertAlmostEqual(analyzer.revenue_churn_rate(START, END), 1 - waterfall['grr'])
        self.assertEqual(waterfall['nrr'], 0.7)


if __name__ == '__main__':
    unittest.main()

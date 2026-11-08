"""Realized cohort LTV is gross profit per acquired customer."""
import importlib.util
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/cfo-advisor/scripts/unit_economics_analyzer.py'
SPEC = importlib.util.spec_from_file_location('realized_cohort_ltv', PATH)
units = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = units
SPEC.loader.exec_module(units)


def cohort(customers=10, revenue=None, margin=0.6):
    if revenue is None:
        revenue = [100 * customers] * 12
    return units.CohortData('Example', '2025', customers, 100 * customers,
                            revenue, margin)


class RealizedLtvTests(unittest.TestCase):
    def test_realized_ltv_is_per_customer(self):
        result = units.analyze_cohort(cohort())
        self.assertEqual(result.m12_ltv, 720)
        self.assertEqual(result.arpa, 100)
        self.assertEqual(result.cac, 100)

    def test_scaling_identical_customers_does_not_scale_ltv(self):
        for customers in (1, 2, 10, 100, 1000):
            with self.subTest(customers=customers):
                self.assertEqual(units.analyze_cohort(cohort(customers)).m12_ltv, 720)

    def test_single_customer_uses_all_gross_profit(self):
        result = units.analyze_cohort(cohort(1, [100] * 12, 0.75))
        self.assertEqual(result.m12_ltv, 900)

    def test_less_than_twelve_months_remains_unavailable(self):
        for months in range(12):
            with self.subTest(months=months):
                self.assertIsNone(units.analyze_cohort(cohort(revenue=[1000] * months)).m12_ltv)

    def test_revenue_after_month_twelve_is_excluded(self):
        result = units.analyze_cohort(cohort(revenue=[1000] * 12 + [1_000_000] * 12))
        self.assertEqual(result.m12_ltv, 720)
        self.assertEqual(result.m24_revenue, 1_000_000)

    def test_nonuniform_revenue_is_realized_not_projected(self):
        result = units.analyze_cohort(cohort(3, list(range(100, 1300, 100)), 0.75))
        self.assertEqual(result.m12_ltv, 1950)
        self.assertEqual(result.m12_revenue, 1200)

    def test_zero_revenue_or_margin_is_zero_ltv(self):
        for value in (cohort(revenue=[0] * 12), cohort(margin=0)):
            with self.subTest(value=value):
                self.assertEqual(units.analyze_cohort(value).m12_ltv, 0)

    def test_zero_customers_rejection_is_preserved(self):
        with self.assertRaisesRegex(ValueError, 'customers_acquired cannot be 0'):
            units.analyze_cohort(cohort(0))


if __name__ == '__main__':
    unittest.main()

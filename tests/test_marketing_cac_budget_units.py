"""CAC is cost per customer, not cost per marketing-qualified lead."""
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/cmo-advisor/scripts/marketing_budget_modeler.py'
SPEC = importlib.util.spec_from_file_location('marketing_cac_tool', PATH)
TOOL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TOOL
SPEC.loader.exec_module(TOOL)


def channel(name='A', rate=0.1, capacity=100, cac=1000):
    return TOOL.Channel(name, cac, capacity, rate, 1, 10000)


class CacBudgetUnitTests(unittest.TestCase):
    def test_ten_percent_conversion(self):
        mqls, budgets = TOOL.allocate_mqls([channel()], 100)
        self.assertEqual(mqls, {'A': 100})
        self.assertEqual(budgets, {'A': 10000})

    def test_full_conversion(self):
        self.assertEqual(TOOL.allocate_mqls([channel(rate=1)], 100)[1], {'A': 100000})

    def test_fractional_expected_customers(self):
        self.assertEqual(TOOL.allocate_mqls([channel(rate=0.25)], 3)[1], {'A': 750})

    def test_capacity_multiplier(self):
        mqls, budgets = TOOL.allocate_mqls([channel(capacity=10)], 1000, 0.5)
        self.assertEqual(mqls, {'A': 60})
        self.assertEqual(budgets, {'A': 6000})

    def test_channel_specific_conversion(self):
        chs = [channel('A', 0.1, 1), channel('B', 0.5, 100, 2000)]
        mqls, budgets = TOOL.allocate_mqls(chs, 20)
        self.assertEqual(mqls, {'A': 12, 'B': 8})
        self.assertAlmostEqual(budgets['A'], 1200)
        self.assertEqual(budgets['B'], 8000)

    def test_unallocated_channel(self):
        chs = [channel('A'), channel('B', cac=2000)]
        self.assertEqual(TOOL.allocate_mqls(chs, 10)[1]['B'], 0)

    def test_zero_target(self):
        self.assertEqual(TOOL.allocate_mqls([channel()], 0), ({'A': 0}, {'A': 0.0}))

    def test_default_funnel_scenario_budget(self):
        ch = channel(rate=TOOL.FUNNEL.mql_to_close)
        result = TOOL.build_scenario('Synthetic', [ch], 100, 1, [])
        self.assertAlmostEqual(result.total_budget, 100 * TOOL.FUNNEL.mql_to_close * 1000)
        self.assertEqual(result.projected_customers, 5)
        self.assertAlmostEqual(result.blended_cac, result.total_budget / 5)


if __name__ == '__main__':
    unittest.main()

"""Detailed reports must label the supplied projection's actual horizon."""
import contextlib
import copy
import importlib.util
import io
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/cmo-advisor/scripts/growth_model_simulator.py'
SPEC = importlib.util.spec_from_file_location('growth_horizon_tool', PATH)
TOOL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TOOL
SPEC.loader.exec_module(TOOL)


def projection(months):
    model = TOOL.GrowthModel('Synthetic', 'Horizon check', {'Events/Field': 1}, 1000000, 0, 1, 1)
    return TOOL.simulate_model(model, months)


def report(proj):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        TOOL.print_model_detail(proj)
    return output.getvalue()


def rows(text):
    return [int(parts[0]) for line in text.splitlines()
            if (parts := line.split()) and parts[0].isdigit()]


class GrowthDetailHorizonTests(unittest.TestCase):
    def test_actual_horizon_label(self):
        text = report(projection(5))
        self.assertIn('Final MRR (5mo):', text)
        self.assertNotIn('Final MRR (18mo):', text)

    def test_non_quarter_final_row(self):
        self.assertEqual(rows(report(projection(5))), [3, 5])

    def test_beyond_global_horizon(self):
        self.assertEqual(rows(report(projection(23))), [3, 6, 9, 12, 15, 18, 21, 23])

    def test_before_first_quarter(self):
        self.assertEqual(rows(report(projection(1))), [1])
        self.assertEqual(rows(report(projection(2))), [2])

    def test_unreached_break_even_horizon(self):
        proj = projection(5)
        self.assertIsNone(proj.break_even_month)
        self.assertIn('CAC break-even:        > 5mo', report(proj))

    def test_known_break_even_preserved(self):
        proj = TOOL.simulate_model(TOOL.GROWTH_MODELS[0], 5)
        self.assertIsNotNone(proj.break_even_month)
        self.assertIn(f'CAC break-even:        Month {proj.break_even_month}', report(proj))

    def test_default_horizon_milestones(self):
        self.assertEqual(rows(report(projection(18))), [3, 6, 9, 12, 15, 18])

    def test_report_does_not_mutate_projection(self):
        proj = projection(5)
        before = copy.deepcopy(proj)
        report(proj)
        self.assertEqual(proj, before)


if __name__ == '__main__':
    unittest.main()

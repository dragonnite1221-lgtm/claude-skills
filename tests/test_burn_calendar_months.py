"""Regression coverage for calendar-month labels in runway forecasts."""
import contextlib
import csv
import importlib.util
import io
import sys
import unittest
from dataclasses import asdict
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/cfo-advisor/scripts/burn_rate_calculator.py'
SPEC = importlib.util.spec_from_file_location('burn_calendar_months', PATH)
burn = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = burn
SPEC.loader.exec_module(burn)


def config(**overrides):
    values = dict(name='Calendar', starting_cash=1_000_000, starting_mrr=100,
                  starting_headcount=1, avg_loaded_salary=1200,
                  base_non_headcount_opex=100, gross_margin_pct=1,
                  mrr_growth_rate=0, model_months=24, start_date=date(2025, 1, 31))
    values.update(overrides)
    return burn.ModelConfig(**values)


class CalendarMonthTests(unittest.TestCase):
    def test_twenty_four_months_do_not_skip_august(self):
        rows = burn.RunwayCalculator(config()).run()
        self.assertEqual(rows[19].label, 'Month 20 (Aug 2026)')
        self.assertEqual(rows[-1].label, 'Month 24 (Dec 2026)')

    def test_leap_february_and_year_rollover(self):
        rows = burn.RunwayCalculator(config(start_date=date(2023, 12, 31), model_months=4)).run()
        self.assertEqual([r.label for r in rows], [
            'Month 01 (Dec 2023)', 'Month 02 (Jan 2024)',
            'Month 03 (Feb 2024)', 'Month 04 (Mar 2024)'])

    def test_start_day_does_not_shift_month(self):
        first = burn.RunwayCalculator(config(start_date=date(2024, 2, 1))).run()
        last = burn.RunwayCalculator(config(start_date=date(2024, 2, 29))).run()
        self.assertEqual([asdict(r) for r in first], [asdict(r) for r in last])

    def test_undated_labels_are_preserved(self):
        rows = burn.RunwayCalculator(config(start_date=None)).run()
        self.assertEqual([r.label for r in rows], [f'Month {n:02d}' for n in range(1, 25)])

    def test_financial_fields_do_not_depend_on_dates(self):
        dated = burn.RunwayCalculator(config(mrr_growth_rate=0.1)).run()
        undated = burn.RunwayCalculator(config(mrr_growth_rate=0.1, start_date=None)).run()
        for first, second in zip(dated, undated):
            a, b = asdict(first), asdict(second)
            a.pop('label'); b.pop('label')
            self.assertEqual(a, b)

    def test_cash_out_and_report_labels_agree(self):
        calc = burn.RunwayCalculator(config(starting_cash=2400))
        rows = calc.run()
        label = 'Month 24 (Dec 2026)'
        self.assertEqual(calc.cash_out_date(rows), label)
        payload = burn.results_to_json([('Calendar', rows, calc)])['scenarios'][0]
        self.assertEqual(payload['cash_out'], label)
        self.assertEqual(payload['monthly'][-1]['label'], label)
        exported = list(csv.DictReader(io.StringIO(burn.export_csv([('Calendar', rows)]))))
        self.assertEqual(exported[-1]['Label'], label)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            burn.print_summary('Calendar', rows, calc)
            burn.print_monthly_table(rows)
        self.assertIn(label, out.getvalue())
        self.assertNotIn('Jan 2027', out.getvalue())

    def test_json_date_input(self):
        values = asdict(config())
        values['start_date'] = '2025-01-31'
        cfg = burn.configs_from_json(values)[0]
        self.assertEqual(burn.RunwayCalculator(cfg).run()[-1].label, 'Month 24 (Dec 2026)')


if __name__ == '__main__':
    unittest.main()

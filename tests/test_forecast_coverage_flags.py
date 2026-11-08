"""Forecast health flags use the same filtered coverage as the report."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'c-level-advisor/cro-advisor/scripts/revenue_forecast_model.py'
SPEC = importlib.util.spec_from_file_location('forecast_coverage_tool', SCRIPT)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)
CRITICAL = 'Pipeline coverage below 2x'
THIN = 'Pipeline coverage below 3x'


def deal(value, close='2026-03-15', stage='proposal'):
    return TOOL.Deal(str(value), 'Example', stage, value, close)


def report(deals, quota=100, quarter='Q1 2026'):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        TOOL.print_report(TOOL.ForecastEngine(deals), quota=quota, current_quarter=quarter)
    return output.getvalue()


class ForecastCoverageFlagTests(unittest.TestCase):
    def test_other_quarters_do_not_hide_shortfall(self):
        text = report([deal(100), deal(1000, '2026-04-15')])
        self.assertIn('Coverage ratio:  1.0x', text)
        self.assertIn(CRITICAL, text)
        self.assertNotIn(THIN, text)

    def test_zero_selected_quarter_is_critical(self):
        text = report([deal(1000, '2026-04-15')])
        self.assertIn('Coverage ratio:  0.0x', text)
        self.assertIn(CRITICAL, text)

    def test_no_open_pipeline_is_critical(self):
        for deals in ([], [deal(1000, stage='closed_won')], [deal(1000, stage='closed_lost')]):
            with self.subTest(deals=deals):
                self.assertIn(CRITICAL, report(deals))

    def test_two_times_coverage_is_thin(self):
        text = report([deal(200), deal(1000, '2026-04-15')])
        self.assertNotIn(CRITICAL, text)
        self.assertIn(THIN, text)

    def test_three_times_coverage_is_healthy(self):
        text = report([deal(300)])
        self.assertNotIn(CRITICAL, text)
        self.assertNotIn(THIN, text)

    def test_no_filter_uses_all_pipeline(self):
        text = report([deal(100), deal(1000, '2026-04-15')], quarter=None)
        self.assertIn('Coverage ratio:  11.0x', text)
        self.assertNotIn(CRITICAL, text)
        self.assertNotIn(THIN, text)

    def test_no_quota_omits_coverage_flags(self):
        for quota in (None, 0):
            with self.subTest(quota=quota):
                text = report([], quota=quota)
                self.assertNotIn(CRITICAL, text)
                self.assertNotIn(THIN, text)

    def test_zero_value_open_deal_is_critical(self):
        text = report([deal(0)])
        self.assertIn('Coverage ratio:  0.0x', text)
        self.assertIn(CRITICAL, text)


if __name__ == '__main__':
    unittest.main()

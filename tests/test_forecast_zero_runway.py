"""Show a computed zero cash runway instead of hiding it."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / (
    "finance/financial-analyst/scripts/forecast_builder.py"
)
SPEC = importlib.util.spec_from_file_location("forecast_builder", SCRIPT)
FORECAST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FORECAST)


def forecast(opening, payroll=100):
    builder = FORECAST.ForecastBuilder({"cash_flow_inputs": {
        "opening_cash_balance": opening, "weekly_payroll": payroll,
    }})
    return builder, builder.run_full_forecast()


class ZeroRunwayTests(unittest.TestCase):
    def test_exact_zero_runway_is_visible(self):
        builder, result = forecast(1300)
        self.assertEqual(result["rolling_cash_flow"]["cash_runway_weeks"], 0)
        self.assertIn("Cash Runway:     0 weeks", builder.format_text(result))

    def test_rounded_zero_runway_is_visible(self):
        builder, result = forecast(1349)
        self.assertEqual(result["rolling_cash_flow"]["closing_balance"], 49)
        self.assertEqual(result["rolling_cash_flow"]["cash_runway_weeks"], 0)
        self.assertIn("Cash Runway:     0 weeks", builder.format_text(result))

    def test_undefined_runway_stays_omitted(self):
        builder, result = forecast(100, payroll=0)
        self.assertIsNone(result["rolling_cash_flow"]["cash_runway_weeks"])
        self.assertNotIn("Cash Runway:", builder.format_text(result))

    def test_positive_runway_stays_visible(self):
        builder, result = forecast(1500)
        self.assertIn("Cash Runway:     2 weeks", builder.format_text(result))

    def test_negative_runway_policy_is_unchanged(self):
        builder, result = forecast(1200)
        self.assertIn("Cash Runway:     -1 weeks", builder.format_text(result))

    def test_missing_metric_stays_omitted(self):
        builder, result = forecast(1300)
        del result["rolling_cash_flow"]["cash_runway_weeks"]
        self.assertNotIn("Cash Runway:", builder.format_text(result))

    def test_cash_flow_numbers_remain_consistent(self):
        _, result = forecast(1300)
        cash = result["rolling_cash_flow"]
        self.assertEqual(cash["closing_balance"], 0)
        self.assertEqual(cash["total_outflows"], 1300)
        self.assertEqual(cash["net_change"], -1300)
        self.assertEqual(len(cash["weekly_projections"]), 13)

    def test_file_cli_text_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forecast.json"
            for opening in [1300, 1349]:
                path.write_text(json.dumps({"cash_flow_inputs": {
                    "opening_cash_balance": opening, "weekly_payroll": 100,
                }}))
                for mode in ["text", "json"]:
                    result = subprocess.run([sys.executable, "-B", str(SCRIPT),
                                             str(path), "--format", mode],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    if mode == "text":
                        self.assertIn("Cash Runway:     0 weeks", result.stdout)
                    else:
                        self.assertEqual(json.loads(result.stdout)["rolling_cash_flow"]
                                         ["cash_runway_weeks"], 0)


if __name__ == "__main__":
    unittest.main()

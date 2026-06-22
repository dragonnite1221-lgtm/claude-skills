# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402


class ForecastBuilderMixin3:
    def build_scenario_comparison(
        self, scenarios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build and compare multiple scenarios."""
        if scenarios is None:
            scenarios = ["base", "bull", "bear"]

        scenario_results: Dict[str, Any] = {}

        for scenario in scenarios:
            scenario_results[scenario] = self.build_driver_based_forecast(scenario)

        # Comparison summary
        comparison: List[Dict[str, Any]] = []
        for scenario in scenarios:
            result = scenario_results[scenario]
            comparison.append({
                "scenario": scenario,
                "total_revenue": result["total_revenue"],
                "total_operating_income": result["total_operating_income"],
                "growth_rate": result["growth_rate"],
                "gross_margin": result["gross_margin"],
                "avg_monthly_revenue": result["average_monthly_revenue"],
            })

        return {
            "scenarios": scenario_results,
            "comparison": comparison,
        }
    def run_full_forecast(
        self, scenarios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run the complete forecast analysis."""
        trends = self.analyze_trends()
        scenario_comparison = self.build_scenario_comparison(scenarios)
        cash_flow = self.build_rolling_cash_flow()

        return {
            "trend_analysis": trends,
            "scenario_comparison": scenario_comparison,
            "rolling_cash_flow": cash_flow,
        }

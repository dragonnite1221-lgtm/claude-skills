# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402
from forecast_builder_p0 import safe_divide  # noqa: F401,E501


class ForecastBuilderMixin1:
    def build_driver_based_forecast(
        self, scenario: str = "base"
    ) -> Dict[str, Any]:
        """
        Build a driver-based revenue forecast.

        Drivers may include: units, price, customers, ARPU, conversion rate, etc.
        """
        scenario_adjustments = self.scenarios_config.get(scenario, {})
        growth_adjustment = scenario_adjustments.get("growth_adjustment", 0.0)
        margin_adjustment = scenario_adjustments.get("margin_adjustment", 0.0)

        base_revenue = 0.0
        if self.historical:
            base_revenue = self.historical[-1].get("revenue", 0)

        # Driver-based calculation
        unit_drivers = self.drivers.get("units", {})
        price_drivers = self.drivers.get("pricing", {})
        customer_drivers = self.drivers.get("customers", {})

        base_growth = self.assumptions.get("revenue_growth_rate", 0.05)
        adjusted_growth = base_growth + growth_adjustment

        base_margin = self.assumptions.get("gross_margin", 0.40)
        adjusted_margin = base_margin + margin_adjustment

        cogs_pct = 1.0 - adjusted_margin
        opex_pct = self.assumptions.get("opex_pct_revenue", 0.25)

        forecast_periods: List[Dict[str, Any]] = []
        current_revenue = base_revenue

        # If we have unit and price drivers, use them
        has_unit_drivers = bool(unit_drivers) and bool(price_drivers)

        if has_unit_drivers:
            base_units = unit_drivers.get("base_units", 1000)
            unit_growth = unit_drivers.get("growth_rate", 0.03) + growth_adjustment
            base_price = price_drivers.get("base_price", 100)
            price_growth = price_drivers.get("annual_increase", 0.02)

            current_units = base_units
            current_price = base_price

            for period in range(1, self.forecast_periods + 1):
                current_units = current_units * (1 + unit_growth / 12)
                if period % 12 == 0:
                    current_price = current_price * (1 + price_growth)

                period_revenue = current_units * current_price
                cogs = period_revenue * cogs_pct
                gross_profit = period_revenue - cogs
                opex = period_revenue * opex_pct
                operating_income = gross_profit - opex

                forecast_periods.append({
                    "period": period,
                    "revenue": round(period_revenue, 2),
                    "units": round(current_units, 0),
                    "price": round(current_price, 2),
                    "cogs": round(cogs, 2),
                    "gross_profit": round(gross_profit, 2),
                    "gross_margin": round(adjusted_margin, 4),
                    "opex": round(opex, 2),
                    "operating_income": round(operating_income, 2),
                })
        else:
            # Simple growth-based forecast
            monthly_growth = (1 + adjusted_growth) ** (1 / 12) - 1

            for period in range(1, self.forecast_periods + 1):
                current_revenue = current_revenue * (1 + monthly_growth)
                cogs = current_revenue * cogs_pct
                gross_profit = current_revenue - cogs
                opex = current_revenue * opex_pct
                operating_income = gross_profit - opex

                forecast_periods.append({
                    "period": period,
                    "revenue": round(current_revenue, 2),
                    "cogs": round(cogs, 2),
                    "gross_profit": round(gross_profit, 2),
                    "gross_margin": round(adjusted_margin, 4),
                    "opex": round(opex, 2),
                    "operating_income": round(operating_income, 2),
                })

        total_revenue = sum(p["revenue"] for p in forecast_periods)
        total_operating_income = sum(p["operating_income"] for p in forecast_periods)

        return {
            "scenario": scenario,
            "growth_rate": round(adjusted_growth, 4),
            "gross_margin": round(adjusted_margin, 4),
            "forecast_periods": forecast_periods,
            "total_revenue": round(total_revenue, 2),
            "total_operating_income": round(total_operating_income, 2),
            "average_monthly_revenue": round(
                safe_divide(total_revenue, len(forecast_periods)), 2
            ),
        }

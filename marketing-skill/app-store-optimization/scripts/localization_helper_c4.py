# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin4:
    def calculate_localization_roi(
        self,
        target_markets: List[str],
        current_monthly_downloads: int,
        localization_cost: float,
        expected_lift_percentage: float = 0.15
    ) -> Dict[str, Any]:
        """
        Estimate ROI of localization investment.

        Args:
            target_markets: List of market codes
            current_monthly_downloads: Current monthly downloads
            localization_cost: Total cost to localize
            expected_lift_percentage: Expected download increase (default 15%)

        Returns:
            ROI analysis
        """
        # Estimate market-specific lift
        market_data = []
        total_expected_lift = 0

        for market_code in target_markets:
            # Find market in priority lists
            market_info = None
            for tier_name, markets in self.PRIORITY_MARKETS.items():
                for m in markets:
                    if m['language'] == market_code:
                        market_info = m
                        break

            if not market_info:
                continue

            # Estimate downloads from this market
            market_downloads = int(current_monthly_downloads * market_info['revenue_share'])
            expected_increase = int(market_downloads * expected_lift_percentage)
            total_expected_lift += expected_increase

            market_data.append({
                'market': market_info['market'],
                'current_monthly_downloads': market_downloads,
                'expected_increase': expected_increase,
                'revenue_potential': market_info['revenue_share']
            })

        # Calculate payback period (assuming $2 revenue per download)
        revenue_per_download = 2.0
        monthly_additional_revenue = total_expected_lift * revenue_per_download
        payback_months = (localization_cost / monthly_additional_revenue) if monthly_additional_revenue > 0 else float('inf')

        return {
            'markets_analyzed': len(market_data),
            'market_breakdown': market_data,
            'total_expected_monthly_lift': total_expected_lift,
            'expected_monthly_revenue_increase': f"${monthly_additional_revenue:,.2f}",
            'localization_cost': f"${localization_cost:,.2f}",
            'payback_period_months': round(payback_months, 1) if payback_months != float('inf') else 'N/A',
            'annual_roi': f"{((monthly_additional_revenue * 12 - localization_cost) / localization_cost * 100):.1f}%" if payback_months != float('inf') else 'Negative',
            'recommendation': self._generate_roi_recommendation(payback_months)
        }
    def _estimate_translation_cost(self, language: str) -> Dict[str, float]:
        """Estimate translation cost for a language."""
        # Base cost per word (professional translation)
        base_cost_per_word = 0.12

        # Language-specific multipliers
        multipliers = {
            'zh-CN': 1.5,  # Chinese requires specialist
            'ja-JP': 1.5,  # Japanese requires specialist
            'ko-KR': 1.3,
            'ar-SA': 1.4,  # Arabic (right-to-left)
            'default': 1.0
        }

        multiplier = multipliers.get(language, multipliers['default'])

        # Typical word counts for app store metadata
        typical_word_counts = {
            'title': 5,
            'subtitle': 5,
            'description': 300,
            'keywords': 20,
            'screenshots': 50  # Caption text
        }

        total_words = sum(typical_word_counts.values())
        estimated_cost = total_words * base_cost_per_word * multiplier

        return {
            'cost_per_word': base_cost_per_word * multiplier,
            'total_words': total_words,
            'estimated_cost': round(estimated_cost, 2)
        }
    def _estimate_total_localization_cost(self, markets: List[Dict[str, Any]]) -> str:
        """Estimate total cost for multiple markets."""
        total = sum(m['estimated_translation_cost']['estimated_cost'] for m in markets)
        return f"${total:,.2f}"

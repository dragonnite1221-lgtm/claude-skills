# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin0:
    """Helps manage multi-language ASO optimization."""
    PRIORITY_MARKETS = {
        'tier_1': [
            {'language': 'en-US', 'market': 'United States', 'revenue_share': 0.25},
            {'language': 'zh-CN', 'market': 'China', 'revenue_share': 0.20},
            {'language': 'ja-JP', 'market': 'Japan', 'revenue_share': 0.10},
            {'language': 'de-DE', 'market': 'Germany', 'revenue_share': 0.08},
            {'language': 'en-GB', 'market': 'United Kingdom', 'revenue_share': 0.06}
        ],
        'tier_2': [
            {'language': 'fr-FR', 'market': 'France', 'revenue_share': 0.05},
            {'language': 'ko-KR', 'market': 'South Korea', 'revenue_share': 0.05},
            {'language': 'es-ES', 'market': 'Spain', 'revenue_share': 0.03},
            {'language': 'it-IT', 'market': 'Italy', 'revenue_share': 0.03},
            {'language': 'pt-BR', 'market': 'Brazil', 'revenue_share': 0.03}
        ],
        'tier_3': [
            {'language': 'ru-RU', 'market': 'Russia', 'revenue_share': 0.02},
            {'language': 'es-MX', 'market': 'Mexico', 'revenue_share': 0.02},
            {'language': 'nl-NL', 'market': 'Netherlands', 'revenue_share': 0.02},
            {'language': 'sv-SE', 'market': 'Sweden', 'revenue_share': 0.01},
            {'language': 'pl-PL', 'market': 'Poland', 'revenue_share': 0.01}
        ]
    }
    CHAR_MULTIPLIERS = {
        'en': 1.0,
        'zh': 0.6,  # Chinese characters are more compact
        'ja': 0.7,  # Japanese uses kanji
        'ko': 0.8,  # Korean is relatively compact
        'de': 1.3,  # German words are typically longer
        'fr': 1.2,  # French tends to be longer
        'es': 1.1,  # Spanish slightly longer
        'pt': 1.1,  # Portuguese similar to Spanish
        'ru': 1.1,  # Russian similar length
        'ar': 1.0,  # Arabic varies
        'it': 1.1   # Italian similar to Spanish
    }
    def __init__(self, app_category: str = 'general'):
        """
        Initialize localization helper.

        Args:
            app_category: App category to prioritize relevant markets
        """
        self.app_category = app_category
        self.localization_plans = []
    def identify_target_markets(
        self,
        current_market: str = 'en-US',
        budget_level: str = 'medium',
        target_market_count: int = 5
    ) -> Dict[str, Any]:
        """
        Recommend priority markets for localization.

        Args:
            current_market: Current/primary market
            budget_level: 'low', 'medium', or 'high'
            target_market_count: Number of markets to target

        Returns:
            Prioritized market recommendations
        """
        # Determine tier priorities based on budget
        if budget_level == 'low':
            priority_tiers = ['tier_1']
            max_markets = min(target_market_count, 3)
        elif budget_level == 'medium':
            priority_tiers = ['tier_1', 'tier_2']
            max_markets = min(target_market_count, 8)
        else:  # high budget
            priority_tiers = ['tier_1', 'tier_2', 'tier_3']
            max_markets = target_market_count

        # Collect markets from priority tiers
        recommended_markets = []
        for tier in priority_tiers:
            for market in self.PRIORITY_MARKETS[tier]:
                if market['language'] != current_market:
                    recommended_markets.append({
                        **market,
                        'tier': tier,
                        'estimated_translation_cost': self._estimate_translation_cost(
                            market['language']
                        )
                    })

        # Sort by revenue share and limit
        recommended_markets.sort(key=lambda x: x['revenue_share'], reverse=True)
        recommended_markets = recommended_markets[:max_markets]

        # Calculate potential ROI
        total_potential_revenue_share = sum(m['revenue_share'] for m in recommended_markets)

        return {
            'recommended_markets': recommended_markets,
            'total_markets': len(recommended_markets),
            'estimated_total_revenue_lift': f"{total_potential_revenue_share*100:.1f}%",
            'estimated_cost': self._estimate_total_localization_cost(recommended_markets),
            'implementation_priority': self._prioritize_implementation(recommended_markets)
        }
